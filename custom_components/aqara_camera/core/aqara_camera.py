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
    CONF_MODEL,
    ERROR_AQARA_CAMERA_UNAVAILABLE,
    ERROR_AQARA_CAMERA_AUTH,
    AQARA_CAMERA_SUCCESS
)

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


    def get_product_info(self):
        """ get product info"""
        try:
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

