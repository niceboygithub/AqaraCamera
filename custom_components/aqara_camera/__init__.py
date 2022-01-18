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
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant, callback

from .const import (
    DOMAIN,
    CONF_MODEL,
    CONF_STREAM,
    CONF_RTSP_AUTH,
    PLATFORMS
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up foscam from a config entry."""
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
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

