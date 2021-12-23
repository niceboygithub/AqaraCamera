"""This component provides basic support for Aqara Camera."""
from __future__ import annotations

import logging

from homeassistant.components.camera import SUPPORT_STREAM, Camera
from homeassistant.const import CONF_HOST

from .core.aqara_camera import (
    AqaraCamera
)
from .core.exceptions import CannotConnect

from .core.const import CONF_MODEL, CONF_STREAM
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a Aqara camera from a config entry."""

    camera = AqaraCamera(
        config_entry.data[CONF_HOST],
        config_entry.data[CONF_MODEL],
        config_entry.data[CONF_STREAM],
        verbose=False,
    )
    ret = await hass.async_add_executor_job(camera.login)
    if not ret:
        raise CannotConnect

    await hass.async_add_executor_job(camera.get_device_info)

    async_add_entities([HassAqaraCamera(camera, config_entry)])


class HassAqaraCamera(Camera):
    """An implementation of a Aqara Camera."""

    def __init__(self, camera, config_entry):
        """Initialize a Aqara camera."""
        super().__init__()

        self._session = camera
        self._name = config_entry.title
        self._model = config_entry.data[CONF_MODEL]
        self._stream = config_entry.data[CONF_STREAM]
        self._unique_id = config_entry.entry_id
        self._motion_status = 0

    async def async_added_to_hass(self):
        """Handle entity addition to hass."""
        # Get motion detection status
        ret, response = await self.hass.async_add_executor_job(
            self._session.get_product_info
        )

        if ret == -3:
            _LOGGER.info(
                "Can't get motion detection status, camera %s configured with non-admin user",
                self._name,
            )

        elif ret != 0:
            _LOGGER.error(
                "Error getting motion detection status of %s: %s", self._name, ret
            )

        else:
            self._motion_status = response == 1

    @property
    def unique_id(self):
        """Return the entity unique ID."""
        return self._unique_id

    @property
    def supported_features(self):
        """Return supported features."""
        if len(self._session.camera_rtsp_url) >= 1:
            return SUPPORT_STREAM

        return None

    @property
    def motion_detection_enabled(self):
        return False

    @property
    def brand(self):
        return self._session.brand

    @property
    def model(self):
        return self._session.model

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, slugify(f"{self._name}_{self._unique_id}"))
            },
            "name": self._name,
            "manufacturer": self._session.brand,
            "model": self._session.model,
            "sw_version": self._session.fw_version,
        }

    def camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image response from the camera."""
        return None

    async def stream_source(self):
        """Return the stream source."""
        self._session.get_product_info()
        if len(self._session.camera_rtsp_url) >= 1:
            return self._session.camera_rtsp_url

        return None

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name
