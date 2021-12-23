""" Aqara Camera telnet shell """

from telnetlib import Telnet
from typing import Union


class TelnetShell(Telnet):
    """ Telnet Shell """
    _aqara_property = False

    def __init__(self, host: str, password=None, device_name=None):
        """ init """
        super().__init__(host, timeout=3)

        login_name = 'admin'
        if (device_name and any(
                name in device_name for name in ['g3'])):
            self._aqara_property = True
            login_name = 'root'
        self.read_until(b"login: ", timeout=3)
        if (device_name and any(
                name in device_name for name in ['g3'])):
            self._suffix = "/ # "
            if any(name in device_name for name in ['g3']):
                password = '\n'
        if password:
            command = "{}\n".format(login_name)
            self.write(command.encode())
            self.read_until(b"Password: ", timeout=3)
            self.run_command(password)
        else:
            self.run_command(login_name)

        self.run_command("stty -echo")
        if 'g3' in device_name:
            self.run_command("cd /")

    def run_command(self, command: str, as_bytes=False) -> Union[str, bytes]:
        """Run command and return it result."""
        # pylint: disable=broad-except
        aqara_timeout = 10
        if self._aqara_property:
            aqara_timeout = 3
        try:
            self.write(command.encode() + b"\n")
            suffix = "\r\n{}".format(self._suffix)
            raw = self.read_until(suffix.encode(), timeout=aqara_timeout)
        except Exception:
            raw = b''
        return raw if as_bytes else raw.decode()

    def get_prop(self, property_value: str):
        """ get property """
        # pylint: disable=broad-except
        try:
            if self._aqara_property:
                command = "agetprop {}\n\r".format(property_value)
            else:
                command = "getprop {}\n\r".format(property_value)
            ret = self.run_command(command)
            if ret.endswith(self._suffix):
                ret = "".join(ret.rsplit(self._suffix, 1))
            if ret.startswith(self._suffix):
                ret = ret.replace(self._suffix, "", 1)
            return ret.replace("\r", "").replace("\n", "")
        except Exception:
            return ''

    def set_prop(self, property_value: str, value: str):
        """ set property """
        if self._aqara_property:
            command = "asetprop {} {}\n".format(property_value, value)
        else:
            command = "setprop {} {}\n".format(property_value, value)
        self.write(command.encode() + b"\n")
        self.read_until(self._suffix.encode())
        self.read_until(self._suffix.encode())

    def get_version(self):
        """ get camera version """
        return self.get_prop("ro.sys.fw_ver")
