"""Constants for Aqara Camera component."""
import voluptuous as vol
from dataclasses import dataclass

from homeassistant.helpers import config_validation as cv
from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_RUNNING,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    SensorEntityDescription,
)
from homeassistant.const import Platform, ENTITY_CATEGORY_DIAGNOSTIC
from homeassistant.helpers.entity import EntityDescription

from .core.const import (
    STREAM_MAIN,
    STREAM_SUB,
    STREAM_SUB2
)


DOMAIN = "aqara_camera"

CONF_STREAM = "stream"
CONF_MODEL = "model"
CONF_RTSP_AUTH ="rtsp_auth"

STREAMS = [STREAM_MAIN, STREAM_SUB, STREAM_SUB2]

OPT_DEVICE_NAME = {
    'g3': "Aqara Camera Hub G3"
}

PLATFORMS = [Platform.CAMERA, Platform.BINARY_SENSOR, Platform.SENSOR]

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


@dataclass
class AqaraPropteries:
    """ Aqara properties"""
    property: str

@dataclass
class AqaraEntityDescription(EntityDescription, AqaraPropteries):
    """Generic Aqara entity description."""

@dataclass
class AqaraSensorEntityDescription(
    SensorEntityDescription, AqaraEntityDescription
):
    """Describes Aqara sensor entity."""

@dataclass
class AqaraBinarySensorEntityDescription(
    BinarySensorEntityDescription, AqaraEntityDescription
):
    """Describes Aqara sensor entity."""

# Binary sensors
CAMERA_BINARY_SENSORS: tuple[AqaraBinarySensorEntityDescription, ...] = (
    AqaraBinarySensorEntityDescription(
        property="camera_avdt_motion_active",
        key="avdt_motion",
        name="Motion",
        device_class=DEVICE_CLASS_RUNNING,
    ),
    AqaraBinarySensorEntityDescription(
        property="camera_avdt_voice_active",
        key="avdt_voice",
        name="Voice",
        device_class=DEVICE_CLASS_RUNNING,
    ),
)

# Sensors
CAMERA_EVENT_SENSORS: tuple[AqaraSensorEntityDescription, ...] = (
    AqaraSensorEntityDescription(
        property="camera_ai_pet_active",
        key="ai_pet",
        name="AI Pet",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    AqaraSensorEntityDescription(
        property="camera_ai_face_active",
        key="ai_face",
        name="Ai Face",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    AqaraSensorEntityDescription(
        property="camera_ai_gesture_active",
        key="ai_gesture",
        name="AI Gesture",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    AqaraSensorEntityDescription(
        property="camera_ai_figure_active",
        key="ai_figure",
        name="AI Figure",
        entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
)

RES_MAPPING = {
    "ai_pet": "13.98.85"
}
