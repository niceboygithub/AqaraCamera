"""Support for Aqara Binary sensors."""
from __future__ import annotations

from typing import Any
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.util.dt import utcnow
from homeassistant.const import CONF_HOST, CONF_NAME

from .core.aqara_camera import (
    AqaraCamera
)
from .core.exceptions import CannotConnect

from . import CameraBaseSensor
from .const import (
    CAMERA_BINARY_SENSORS,
    CONF_MODEL,
    CONF_STREAM,
    DOMAIN,
    AqaraBinarySensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Aqara Binary Sensor."""

    camera = hass.data[DOMAIN][config_entry.entry_id].get("camera", None)
    if not camera:
        camera = AqaraCamera(
            hass,
            config_entry.data[CONF_HOST],
            config_entry.data[CONF_MODEL],
            config_entry.data[CONF_STREAM],
            verbose=False,
        )
        ret = camera.connect()
        if not ret:
            raise CannotConnect

    device = camera.get_device_info()
    if CONF_NAME not in device:
        _LOGGER.error("Can not connect to Aqara Camera")
        return
    device["entry_id"] = config_entry.entry_id

    try:
        entities = []
        entities.extend(
            [
                CameraEventBinarySensor(camera, device, description)
                for description in CAMERA_BINARY_SENSORS
                if camera.properties.get(description.property, 'false') == 'true'
            ]
        )

        async_add_entities(entities)
    except AttributeError as err:
        _LOGGER.error(err)


class CameraBinarySensor(CameraBaseSensor, BinarySensorEntity):
    """ for binary sensor specific attributes."""

    entity_description: AqaraBinarySensorEntityDescription

    def __init__(
        self,
        camera: AqaraCamera,
        device: dict,
        description: AqaraBinarySensorEntityDescription,
    ) -> None:
        """Initialize the Camera sensor entity."""
        super().__init__(camera, device, description)


class CameraEventBinarySensor(CameraBinarySensor):
    """Representation a Camera event binary sensor."""

    def __init__(
        self,
        camera: AqaraCamera,
        device: dict,
        description: AqaraBinarySensorEntityDescription,
    ) -> None:
        """Initialize the Camera Event Binary Sensor entity."""
        self._should_poll = False
        super().__init__(camera, device, description)

    @property
    def should_poll(self) -> bool:
        """Poll state from device."""
        return self._should_poll

    @property
    def native_value(self) -> Any | None:
        """Return the state."""
        _LOGGER.error("native_value {}".format(self._attr_name))
        return None
        attr = getattr(self._camera, self.entity_description.key)
        if attr is None:
            return None

        return attr

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return info details."""
        attr = self._attr_extra_state_attributes
        return attr
