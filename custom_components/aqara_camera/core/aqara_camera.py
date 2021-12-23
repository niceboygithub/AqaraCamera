"""Class for Aqara Camera component."""
import socket
import json
import logging

from homeassistant.const import (
    CONF_HOST,
    CONF_NAME
)

from .shell import TelnetShell

from .const import (
    ATTR_ANGLE_X,
    ATTR_ANGLE_Y,
    ATTR_SPAN_X,
    ATTR_SPAN_Y,
    CONF_MODEL,
    DIR_UP,
    DIR_DOWN,
    DIR_LEFT,
    DIR_RIGHT,
    ERROR_AQARA_CAMERA_UNAVAILABLE,
    ERROR_AQARA_CAMERA_AUTH,
    AQARA_CAMERA_SUCCESS
)
MD5_MI_MOTOR_ARMV7L = "b363f3ad671f7d854ef168e680eb8d3e"

_LOGGER = logging.getLogger(__name__)


class AqaraCamera():
    """ Aqara Camera main class """

    def __init__(self, host, model, stream, verbose=False):
        """ init """
        self._shell = None
        self._host = host
        self._device_name = model
        self._stream = stream
        self._debug = verbose
        self._brand = ""
        self._fw_version = ""
        self._model = ""
        self._mi_motor = False
        self.rtsp_url = ""

    @property
    def brand(self):
        """ return rtsp url """
        return self._brand

    @property
    def model(self):
        """ return rtsp url """
        return self._model

    @property
    def fw_version(self):
        """ return rtsp url """
        return self._fw_version

    @property
    def camera_rtsp_url(self):
        """ return rtsp url """
        return self.rtsp_url

    def debug(self, message: str):
        """ deubug function """
        if self._debug:
            _LOGGER.debug(f"{self._host}: {message}")

    def login(self):
        """ login """
        try:
            shell = TelnetShell(self._host, None, self._device_name)

        except (ConnectionRefusedError, socket.timeout):
            return False

        except Exception as err:
            self.debug(f"Can't prepare camera: {err}")
            return False
        self._shell = shell
        return True

    def run_command(self, command: str):
        """ run command """
        fix = self._shell.suffix
        ret = self._shell.run_command(command)
        if ret.endswith(fix):
            ret = "".join(ret.rsplit(fix, 1))
        if ret.startswith(fix):
            ret = ret.replace(fix, "", 1)
        return ret

    def get_product_info(self):
        """ get product info"""
        try:
            if self._shell.file_exist("/data/bin/mi_motor"):
                self._mi_motor = True
            raw = self._shell.get_prop("sys.camera_rtsp_url")
            camera_rtsp_url = json.loads(raw.replace(r"\/", "/"))
        except Exception as err:
            return ERROR_AQARA_CAMERA_UNAVAILABLE, err

        if len(camera_rtsp_url) >= 1:
            if self._stream == "sub2":
                self.rtsp_url = camera_rtsp_url["360p"]
            elif self._stream == "sub":
                self.rtsp_url = camera_rtsp_url["720p"]
            else:
                self.rtsp_url = camera_rtsp_url["1080p"]
            return AQARA_CAMERA_SUCCESS, ""
        return ERROR_AQARA_CAMERA_UNAVAILABLE, ""

    def get_device_info(self):
        """ get device info """
        result = {}

        model = self._shell.get_prop("persist.sys.model")
        name = self._shell.get_prop("ro.sys.name")
        mac = self._shell.get_prop("persist.sys.miio_mac")
        result[CONF_NAME] = "{}-{}".format(
            name, mac[-5:].upper().replace(":", ""))
        result[CONF_MODEL] = model
        self._fw_version = self._shell.get_prop("ro.sys.fw_ver")
        self._brand = self._shell.get_prop("ro.sys.manufacturer")
        self._model = self._shell.get_prop("ro.sys.product")
        return result

    def prepare(self):
        """ prepare camera """
        self._shell.check_bin('mi_motor', MD5_MI_MOTOR_ARMV7L , 'bin/armv7l/mi_motor')

    def ptz_control(self, direction, span_x, span_y):
        """ ptz control """
        if not self._mi_motor:
            _LOGGER.error("mi_motor is not exist!")
            return
        try:
            command = "/data/bin/mi_motor -g\n"
            ret = self.run_command(command)
            motor_info = json.loads(ret)

            current_angle_x = motor_info[ATTR_ANGLE_X]
            current_angle_y = motor_info[ATTR_ANGLE_Y]
            if direction.lower() == DIR_UP:
                current_angle_y += 3
            if direction.lower() == DIR_DOWN:
                current_angle_y -= 3
            if direction.lower() == DIR_LEFT:
                current_angle_x += 3
            if direction.lower() == DIR_RIGHT:
                current_angle_x -= 3
            self._shell.set_prop("sys.sys.camera_ptz_moving", "true")
            command = "/data/bin/mi_motor -x {} -y {} -a {} -b {}\n".format(
                current_angle_x, current_angle_y, span_x, span_y
            )
            ret = self.run_command(command)
        except Exception as err:
            self.debug(f"ptz_control got error: {err}")
        self._shell.set_prop("sys.sys.camera_ptz_moving", "false")

    def ptz_control_preset(self, angle_x, angle_y, span_x, span_y):
        """ ptz control preset """
        if not self._mi_motor:
            _LOGGER.error("mi_motor is not exist!")
            return
        try:
            if (angle_x is None and angle_y is None and
                    span_x is None and span_y is None):
                return
            command = "/data/bin/mi_motor -g\n"
            ret = self.run_command(command)
            motor_info = json.loads(ret)
            current_angle_x = motor_info[ATTR_ANGLE_X]
            current_angle_y = motor_info[ATTR_ANGLE_Y]
            current_span_x = motor_info[ATTR_SPAN_X]
            current_span_y = motor_info[ATTR_SPAN_Y]
            if angle_x is None:
                angle_x = current_angle_x
            if angle_y is None:
                angle_y = current_angle_y
            if span_x is None:
                span_x = current_span_x
            if span_y is None:
                span_y = current_span_y
            self._shell.set_prop("sys.sys.camera_ptz_moving", "true")
            command = "/data/bin/mi_motor -x {} -y {} -a {} -b {}\n".format(
                angle_x, angle_y, span_x, span_y
            )
            ret = self.run_command(command)
        except Exception as err:
            self.debug(f"ptz_control_preset got error: {err}")
        self._shell.set_prop("sys.sys.camera_ptz_moving", "false")
