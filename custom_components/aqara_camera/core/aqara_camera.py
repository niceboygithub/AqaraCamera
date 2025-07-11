"""Class for Aqara Camera component."""
import socket
import time
import json
import re
import logging

from homeassistant.const import (
    CONF_NAME
)

from .shell import TelnetShell, TelnetShellG3

from .const import (
    STREAM_SUB,
    STREAM_SUB2,
    ANGLE_X,
    ANGLE_Y,
    SPAN_X,
    SPAN_Y,
    CONF_MODEL,
    CONF_RTSP_AUTH,
    DIR_UP,
    DIR_DOWN,
    DIR_LEFT,
    DIR_RIGHT,
    ERROR_AQARA_CAMERA_UNAVAILABLE,
    ERROR_AQARA_CAMERA_AUTH,
    AQARA_CAMERA_SUCCESS,
    PERSIST_REC_MODE,
    SYS_PTZ_MOVING,
    MD5_MI_MOTOR_ARMV7L
)

_LOGGER = logging.getLogger(__name__)


class AqaraCamera():
    """ Aqara Camera main class """

    def __init__(self, hass, host, model, stream, verbose=False):
        """ init """
        self._shell = None
        self._host = host
        self._device_name = model
        self._stream = stream
        self._debug = verbose
        self._mi_motor = False
        self._rtsp_auth = True  # for fast access
        self._properties: dict = {}

        self.hass = hass
        self.rtsp_url = ""

    @property
    def brand(self):
        """ return brand """
        return self._properties["ro.sys.manufacturer"]

    @property
    def model(self):
        """ return model """
        return self._properties["ro.sys.product"]

    @property
    def fw_version(self):
        """ return firmware version """
        return self._properties["ro.sys.fw_ver"]

    @property
    def properties(self):
        """ return camera properties """
        properties = {}
        for key, value in self._properties.items():
            if "camera_ai" in key:
                properties[key.replace(
                    "persist.app.camera_", "").replace(
                        "sys.camera_", "")] = value
        return properties

    @property
    def camera_rtsp_url(self):
        """ return rtsp url """
        return self.rtsp_url

    @property
    def is_recording(self):
        """ return is_recording """
        raw = self._shell.get_prop(PERSIST_REC_MODE)
        if raw != "0":
            return True
        return False

    def debug(self, message: str):
        """ deubug function """
        if self._debug:
            _LOGGER.debug(f"{self._host}: {message}")

    def connect(self):
        """ login """
        try:
            if any(name in self._device_name for name in ['g3']):
                shell = TelnetShellG3(self._host)
            else:
                shell = TelnetShell(self._host)

            if shell.login():
                self._shell = shell

            if self._shell.file_exist("/data/bin/mi_motor"):
                self._mi_motor = True

        except (ConnectionRefusedError, socket.timeout) as err:
            self.debug(f"Can't prepare camera: {err}")
            return False

        except Exception as err:
            self.debug(f"Can't prepare camera: {err}")
            return False
        return (self._shell != None)

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
        """ get product info """
        try:
            raw = self._shell.get_prop("sys.camera_rtsp_url")
            if len(raw) <= 6:
                self._prepare_rtsp(self._rtsp_auth)
                raw = self._shell.get_prop("sys.camera_rtsp_url")
            camera_rtsp_url = json.loads(raw.replace(r"\/ # ", "").replace("~ #", ""))
        except Exception as err:
            return ERROR_AQARA_CAMERA_UNAVAILABLE, err

        if len(camera_rtsp_url) >= 1:
            if self._stream == STREAM_SUB2:
                self.rtsp_url = camera_rtsp_url["360p"]
            elif self._stream == STREAM_SUB:
                self.rtsp_url = camera_rtsp_url["720p"]
            else:
                self.rtsp_url = camera_rtsp_url.get("1080p")
                if not self.rtsp_url:
                    self.rtsp_url = camera_rtsp_url.get("1296p")
                    if not self.rtsp_url:
                        self.rtsp_url = camera_rtsp_url.get("1520p")
                        if not self.rtsp_url:
                            return ERROR_AQARA_CAMERA_UNAVAILABLE, ""

            return AQARA_CAMERA_SUCCESS, ""
        return ERROR_AQARA_CAMERA_UNAVAILABLE, ""

    def _get_all_properties(self):
        """get device all properties"""
        raw = self._shell.get_prop("")

        pattern = r'(\[[^[]+\])'
        matches = re.findall(pattern, raw)
        self._properties = {}
        it_matches = iter(matches)
        while True:
            try:
                x = next(it_matches)
                y = next(it_matches)
                if not y.strip("[").rstrip("]").endswith("..."):
                    self._properties[x.strip("[").rstrip("]")] = y.strip("[").rstrip("]")
            except StopIteration:
                break

    def get_device_info(self):
        """ get device info """
        result = {}
        self._get_all_properties()

        model = self._properties.get("persist.sys.model", None)
        if model is None:
            # Try again
            self._get_all_properties()

        mac = self._properties.get("persist.sys.miio_mac", None)
        name = self._properties.get("ro.sys.name", None)
        if mac and name:
            result[CONF_NAME] = "{}-{}".format(
                name, mac[-5:].upper().replace(":", ""))
            result[CONF_MODEL] = model

        return result

    def _prepare_rtsp(self, rtsp_auth):
        processes = self._shell.get_running_ps()
        if not rtsp_auth:
            if not self._shell.file_exist("/tmp/app_monitor.sh"):
                command = 'sed "s/rtsp -a /rtsp /g" /bin/app_monitor.sh > /tmp/app_monitor.sh'
                self._shell.run_command(command)
                command = "chmod a+x /tmp/app_monitor.sh"
                self._shell.run_command(command)
                command = "pkill app_monitor.sh; /tmp/app_monitor.sh &"
                self._shell.run_command(command)
            if "rtsp -a" in processes:
                command = "pkill rtsp"
                self._shell.run_command(command)
        else:
            if "rtsp -a" not in processes:
                command = "pkill rtsp"
                self._shell.run_command(command)

    def prepare(self, config: dict):
        """ prepare camera """
        self._shell.check_bin('mi_motor', MD5_MI_MOTOR_ARMV7L , 'bin/armv7l/mi_motor')

        POST_INIT_SH = "/data/scripts/post_init.sh"
        if not self._shell.file_exist(POST_INIT_SH):
            command = "mkdir -p /data/scripts"
            self._shell.write(command.encode() + b"\n")
            time.sleep(1)
            command = "echo -e '#!/bin/sh\r\n\r\n " \
                "[ -x /data/bin/mosquitto ] && /data/bin/mosquitto -d" \
                "fw_manager.sh -r\r\n" \
                "asetprop sys.camera_ptz_moving true\r\n" \
                "fw_manager.sh -t -k' > {}".format(POST_INIT_SH)
            self._shell.run_command(command)
            command = "chmod a+x {}".format(POST_INIT_SH)
            self._shell.run_command(command)
            command = "chattr +i {}".format(POST_INIT_SH)
            self._shell.run_command(command)

        self._rtsp_auth = config.get(CONF_RTSP_AUTH, True)
        self._prepare_rtsp(self._rtsp_auth)
        raw = self._shell.get_prop("sys.camera_rtsp_url")
        if len(raw) <= 6:
            self._prepare_rtsp(self._rtsp_auth)

    def ptz_control(self, direction, span_x, span_y):
        """ ptz control """
        if not self._mi_motor:
            _LOGGER.error("mi_motor is not exist!")
            return
        try:
            command = "/data/bin/mi_motor -g\n"
            ret = self.run_command(command)
            motor_info = json.loads(ret)

            current_angle_x = motor_info[ANGLE_X]
            current_angle_y = motor_info[ANGLE_Y]
            if direction.lower() == DIR_UP:
                current_angle_y += 3
            if direction.lower() == DIR_DOWN:
                current_angle_y -= 3
            if direction.lower() == DIR_LEFT:
                current_angle_x += 3
            if direction.lower() == DIR_RIGHT:
                current_angle_x -= 3
            self._shell.set_prop(SYS_PTZ_MOVING, "true")
            command = "/data/bin/mi_motor -x {} -y {} -a {} -b {}\n".format(
                current_angle_x, current_angle_y, span_x, span_y
            )
            ret = self.run_command(command)
        except Exception as err:
            self.debug(f"ptz_control got error: {err}")
        self._shell.set_prop(SYS_PTZ_MOVING, "false")

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
            current_angle_x = motor_info[ANGLE_X]
            current_angle_y = motor_info[ANGLE_Y]
            current_span_x = motor_info[SPAN_X]
            current_span_y = motor_info[SPAN_Y]
            if angle_x is None:
                angle_x = current_angle_x
            if angle_y is None:
                angle_y = current_angle_y
            if span_x is None:
                span_x = current_span_x
            if span_y is None:
                span_y = current_span_y
            self._shell.set_prop(SYS_PTZ_MOVING, "true")
            command = "/data/bin/mi_motor -x {} -y {} -a {} -b {}\n".format(
                angle_x, angle_y, span_x, span_y
            )
            ret = self.run_command(command)
        except Exception as err:
            self.debug(f"ptz_control_preset got error: {err}")
        self._shell.set_prop(SYS_PTZ_MOVING, "false")
