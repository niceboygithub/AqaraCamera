"""Constants for Aqara Camera component."""

from homeassistant.const import Platform

DOMAIN = "aqara_camera"

CONF_STREAM = "stream"
CONF_MODEL = "model"

STREAMS = ["Main", "Sub", "Sub2"]

OPT_DEVICE_NAME = {
    'g3': "Aqara Camera Hub G3"
}

PLATFORMS = [Platform.CAMERA]

ERROR_AQARA_CAMERA_UNAVAILABLE = "unavailable"
ERROR_AQARA_CAMERA_AUTH = "error_auth"
AQARA_CAMERA_SUCCESS = "success"