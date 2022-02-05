"""This component provides basic support for Aqara Camera."""
from __future__ import annotations

import logging
import asyncio

from homeassistant.components import ffmpeg
from homeassistant.components.camera import SUPPORT_STREAM, Camera
from homeassistant.helpers import entity_platform
from homeassistant.components.ffmpeg import DATA_FFMPEG
from homeassistant.util import slugify
from homeassistant.const import CONF_HOST

from .core.aqara_camera import (
    AqaraCamera
)

from .core.const import (
    AQARA_CAMERA_SUCCESS,
    ERROR_AQARA_CAMERA_UNAVAILABLE
)

from .const import (
    CONF_MODEL,
    CONF_STREAM,
    DIR_PRESET,
    DOMAIN,
    SERVICE_PTZ,
    SCHEMA_SERVICE_PTZ,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a Aqara camera from a config entry."""

    camera = hass.data[DOMAIN][config_entry.entry_id].get("camera", None)
    if not camera:
        camera = AqaraCamera(
            hass,
            config_entry.data[CONF_HOST],
            config_entry.data[CONF_MODEL],
            config_entry.data[CONF_STREAM],
            verbose=False,
        )
        ret = await hass.async_add_executor_job(camera.connect)
        if not ret:
            raise CannotConnect

    await hass.async_add_executor_job(camera.get_device_info)

    async_add_entities([HassAqaraCamera(hass, camera, config_entry)])

    platform = entity_platform.current_platform.get()
    platform.async_register_entity_service(
        SERVICE_PTZ, SCHEMA_SERVICE_PTZ, "perform_ptz",
    )

class HassAqaraCamera(Camera):
    """An implementation of a Aqara Camera."""

    def __init__(self, hass, camera, config_entry):
        """Initialize a Aqara camera."""
        super().__init__()

        self._session = camera
        self._name = config_entry.title
        self._model = config_entry.data[CONF_MODEL]
        self._stream = config_entry.data[CONF_STREAM]
        self._unique_id = config_entry.entry_id
        self._motion_status = 0
        self._ffmpeg = hass.data.get(DATA_FFMPEG, None)
        self._attr_supported_features = SUPPORT_STREAM

    async def async_added_to_hass(self):
        """Handle entity addition to hass."""
        # Get product info
        ret, response = await self.hass.async_add_executor_job(
            self._session.get_product_info
        )

        if ret == ERROR_AQARA_CAMERA_UNAVAILABLE:
            _LOGGER.info(
                "Can't get camera status, camera %s configured with non-admin user",
                self._name,
            )

        elif ret != AQARA_CAMERA_SUCCESS:
            _LOGGER.error(
                "Error getting camera status of %s: %s", self._name, ret
            )

        else:
            self._motion_status = response == 1
        self._attr_brand = self._session.brand
        self._attr_model = self._session.model
        self._attr_is_recording = self._session.is_recording
        self._attr_motion_detection_enabled = not self._session.is_recording

    @property
    def unique_id(self):
        """Return the entity unique ID."""
        return self._unique_id

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

    @property
    def extra_state_attributes(self):
        """Return the camera attributes."""
        return {"rtsp_url": self._session.camera_rtsp_url}

    @property
    def name(self):
        """Return the name of this camera."""
        return self._name

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return bytes of camera image."""
        if self._ffmpeg:
            self._session.get_product_info()
            return await ffmpeg.async_get_image(
                self.hass,
                self._session.camera_rtsp_url,
                width=width,
                height=height,
            )
        return None

    async def stream_source(self):
        """Return the stream source."""
        self._session.get_product_info()
        self._attr_is_recording = self._session.is_recording
        if len(self._session.camera_rtsp_url) >= 1:
            return self._session.camera_rtsp_url

        return None

    def perform_ptz(
        self, direction, angle_x=None, angle_y=None, span_x=None, span_y=None
    ):
        """Perform a PTZ action on the camera."""
        if direction.lower() == DIR_PRESET:
            self._session.ptz_control_preset(angle_x, angle_y, span_x, span_y)
        else:
            self._session.ptz_control(direction, span_x, span_y)
