"""The Aqara Camera component."""
import logging

from .core.aqara_camera import (
    ERROR_AQARA_CAMERA_AUTH,
    ERROR_AQARA_CAMERA_UNAVAILABLE,
    AQARA_CAMERA_SUCCESS,
    AqaraCamera
)
from .core.exceptions import CannotConnect, InvalidAuth, InvalidResponse

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback, Event
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.util import slugify
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    EVENT_HOMEASSISTANT_STOP
)

from .const import (
    DOMAIN,
    CONF_MODEL,
    CONF_STREAM,
    CONF_RTSP_AUTH,
    PLATFORMS,
    AqaraSensorEntityDescription
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up aqara camera from a config entry."""
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"config": entry.data}

    camera = AqaraCamera(
        hass,
        entry.data[CONF_HOST],
        entry.data[CONF_MODEL],
        entry.data[CONF_STREAM],
        verbose=False,
    )
    ret = camera.connect()
    if not ret:
        raise CannotConnect

    # Validate data by sending a request to the camera
    ret, _ = camera.get_product_info()

    if ret == ERROR_AQARA_CAMERA_UNAVAILABLE:
        raise CannotConnect

    if ret == ERROR_AQARA_CAMERA_AUTH:
        raise InvalidAuth

    if ret != AQARA_CAMERA_SUCCESS:
        _LOGGER.error(
            "Unexpected error code from camera %s %s",
            entry.data[CONF_HOST],
            ret,
        )
        raise InvalidResponse

    config = {CONF_RTSP_AUTH: entry.data.get(CONF_RTSP_AUTH, True)}
    await hass.async_add_executor_job(camera.prepare, config)

    data = {
        "config": entry.data,
        "camera": camera
    }

    hass.data[DOMAIN][entry.entry_id] = data

    await camera.async_connect()

    async def async_stop_mqtt(_event: Event):
        """Stop MQTT component."""
        await camera.async_disconnect()

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, async_stop_mqtt)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class CameraBaseSensor(Entity):
    """Representation of a Aqara Sensor entry."""
    entity_description: AqaraSensorEntityDescription
    unique_id: str

    def __init__(
        self,
        camera: AqaraCamera,
        device: dict,
        description: AqaraSensorEntityDescription,
    ) -> None:
        """Initialize the Aqara Base Sensor entity."""
        super().__init__()
        self.entity_description = description

        self._camera = camera
        self._device = device
        self._unique_id = device["entry_id"]
        self._attr_name = f"{device[CONF_NAME]} {description.name}"
        self._attr_unique_id: str = (
            f"{device[CONF_NAME]}_{description.key}"
        )
        self._attr_extra_state_attributes = {}

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, slugify(
                f"{self._device[CONF_NAME]}_{self._unique_id}"))},
            name=self._device[CONF_NAME],
            manufacturer=self._camera.brand,
            model=self._camera.model,
            sw_version=self._camera.fw_version
        )
