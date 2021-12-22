"""Config flow for Aqara Camera integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME
)
from homeassistant.data_entry_flow import AbortFlow

from .core.aqara_camera import (
    ERROR_AQARA_CAMERA_AUTH,
    ERROR_AQARA_CAMERA_UNAVAILABLE,
    AQARA_CAMERA_SUCCESS,
    AqaraCamera
)
from .core.exceptions import CannotConnect, InvalidAuth, InvalidResponse

from .core.const import (
    CONF_MODEL,
    CONF_STREAM,
    DOMAIN,
    OPT_DEVICE_NAME,
    STREAMS
)


DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_MODEL, default="g3"): vol.In(OPT_DEVICE_NAME),
        vol.Required(CONF_STREAM, default=STREAMS[0]): vol.In(STREAMS),
    }
)
_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aqara Camera."""

    VERSION = 2

    async def _validate_and_create(self, data):
        """Validate the user input allows us to connect.
        Data has the keys from DATA_SCHEMA with values provided by the user.
        """
        self._async_abort_entries_match(
            {CONF_HOST: data[CONF_HOST]}
        )

        camera = AqaraCamera(
            data[CONF_HOST],
            data[CONF_MODEL],
            data[CONF_STREAM],
            verbose=False,
        )
        ret = await self.hass.async_add_executor_job(camera.login)
        if not ret:
            raise CannotConnect

        # Validate data by sending a request to the camera
        ret, _ = await self.hass.async_add_executor_job(camera.get_product_all_info)

        if ret == ERROR_AQARA_CAMERA_UNAVAILABLE:
            raise CannotConnect

        if ret == ERROR_AQARA_CAMERA_AUTH:
            raise InvalidAuth

        if ret != AQARA_CAMERA_SUCCESS:
            _LOGGER.error(
                "Unexpected error code from camera %s %s",
                data[CONF_HOST],
                ret,
            )
            raise InvalidResponse

        # Try to get camera name
        ret = await self.hass.async_add_executor_job(camera.get_device_info)

        dev_name = f"{ret[CONF_NAME]}"

        name = data.pop(CONF_NAME, dev_name)

        return self.async_create_entry(title=name, data=data)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                return await self._validate_and_create(user_input)

            except CannotConnect:
                errors["base"] = "cannot_connect"

            except InvalidAuth:
                errors["base"] = "invalid_auth"

            except InvalidResponse:
                errors["base"] = "invalid_response"

            except AbortFlow:
                raise

            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

