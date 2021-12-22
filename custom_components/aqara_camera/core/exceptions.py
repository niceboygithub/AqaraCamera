"""Exceptions for Aqara Camera component."""

from homeassistant import exceptions

class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


class InvalidResponse(exceptions.HomeAssistantError):
    """Error to indicate there is invalid response."""

