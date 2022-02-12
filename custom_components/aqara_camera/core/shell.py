""" Aqara Camera telnet shell """

import time
from telnetlib import Telnet
from typing import Union

WGET = "(wget http://master.dl.sourceforge.net/project/aqarahub/{0}?viasf=1 " \
       "-O /data/bin/{1} && chmod +x /data/bin/{1})"


class TelnetShell(Telnet):
    """ Telnet Shell """
    _aqara_property = False

    def __init__(self, host: str, password=None):
        """ init """
        super().__init__(host, timeout=3)
        self._host = host
        self._password = password
        self._suffix = "# "

    def login(self):
        """ login function """
        self.write(b"\n")
        login_name = 'admin'
        self.read_until(b"login: ", timeout=3)
        self.write(login_name.encode() + b"\n")

        if self._password:
            self.read_until(b"Password: ", timeout=3)
            self.run_command(self._password)

        command = "stty -echo"
        self.write(command.encode() + b"\n")
        self.read_until(b"stty -echo\n", timeout=10)
        return True

    @property
    def suffix(self):
        """ return shell extra prefix or suffix"""
        return self._suffix

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

    def file_exist(self, filename: str) -> bool:
        """ check file exit """
        raw = self.run_command("ls -al {}".format(filename))
        if "No such" not in str(raw):
            return True
        return False

    def get_running_ps(self) -> str:
        """ get processes list """
        return self.run_command("ps")

    def check_bin(self, filename: str, md5: str, url=None) -> bool:
        """Check binary md5 and download it if needed."""
        # used * for development purposes
        if url:
            self.run_command("mkdir -p /data/bin\n")
            self.run_command(WGET.format(url, filename))
            return self.check_bin(filename, md5)
        elif md5 in self.run_command("md5sum /data/bin/{}".format(filename)):
            return True
        else:
            return False

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


class TelnetShellG3(TelnetShell):
    """ Telnet Shell """

    def __init__(self, host: str, password=None):
        """ init """
        super().__init__(host, password)
        self._suffix = "/ # "
        self._aqara_property = True

    def login(self):
        """ login function """
        self.write(b"\n")
        self.read_until(b"login: ", timeout=1)

        password = self._password
        if self._password is None:
            password = '\n'

        command = "root"
        self.write(command.encode() + b"\n")
        if password:
            self.read_until(b"Password: ", timeout=1)
            self.write(password.encode() + b"\n")

        command = "stty -echo"
        self.write(command.encode() + b"\n")
        command = "cd /"
        self.write(command.encode() + b"\n")
        self.read_until(b"/ # ", timeout=10)
        return True
