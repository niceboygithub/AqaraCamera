"""Constants for Aqara Camera component."""
import voluptuous as vol

from homeassistant.helpers import config_validation as cv
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

# Services data
DIR_UP = "up"
DIR_DOWN = "down"
DIR_LEFT = "left"
DIR_RIGHT = "right"
DIR_PRESET = "preset"
ATTR_DIRECTION = "direction"
ATTR_ANGLE_X = "angle_x"
ATTR_ANGLE_Y = "angle_y"
ATTR_SPAN_X = "span_x"
ATTR_SPAN_Y = "span_y"

angle_x = vol.All(
    vol.Coerce(float), vol.Range(min=-170, max=170), msg="invalid angle x"
)

angle_y = vol.All(
    vol.Coerce(float), vol.Range(min=-15, max=50), msg="invalid angle y"
)

SERVICE_PTZ = "ptz"
SCHEMA_SERVICE_PTZ = {
        vol.Required(ATTR_DIRECTION): vol.In(
            [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT, DIR_PRESET]
        ),
        vol.Optional(ATTR_ANGLE_X): angle_x,
        vol.Optional(ATTR_ANGLE_Y): angle_y,
        vol.Optional(ATTR_SPAN_X): cv.positive_int,
        vol.Optional(ATTR_SPAN_Y): cv.positive_int
}

