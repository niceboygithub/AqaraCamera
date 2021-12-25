# Aqara Camera G3 integration for Home Assistant

**ATTENTION:** The component **only works after enabled telnet.** Only supportd stream. Not support motion detection, ai etc. yet.

This is a way to [enable telnetd](https://github.com/Wh1terat/aQRootG3) from #Wh1terat. After enabled telnet, you need use putty to telnet <ip of your G3>. Then enter the following commands.

```
chmod a+w /data/scripts/post_init.sh
echo -e "#!/bin/sh\n\nasetprop sys.camera_ptz_moving true\nfw_manager.sh -r\nfw_manager.sh -t -k" > /data/scripts/post_init.sh
chattr +i /data/scripts/post_init.sh
```


## Installation

you can install component with [HACS](https://hacs.xyz),  custom repo: HACS > Integrations > 3 dots (upper top corner) > Custom repositories > URL: `niceboygithub/AqaraCamera` > Category: Integration

Or Download and copy `custom_components/aqara_camera` folder to `custom_components` folder in your HomeAssistant config folder


## Configuration

1. [⚙️ Configuration](https://my.home-assistant.io/redirect/config) > [🧩 Integrations](https://my.home-assistant.io/redirect/integrations) > [➕ Add Integration](https://my.home-assistant.io/redirect/config_flow_start?domain=aqara_camera) > 🔍 Search `Aqara Camera`

    Or click (HA v2021.3.0+): [![add](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=aqara_camera)
   1. If the integration didn't show up in the list please REFRESH the page
   2. If the integration is still not in the list, you need to clear the browser cache.
2. Enter Camera IP address.
3. Click Send button, then wait this integration is configured completely.
4. Done

## Still Image support

Need to add the following information to your configuration.yaml file:

ffmpeg:

Supported Versions
---------------

| Market | Firmware Version | Status |
| -------| --------------- | -- |
| China  | 3.3.2_0019.0004 | :white_check_mark: |
| China  | 3.3.4_0007.0004  | :white_check_mark: |


**Attention:** The component is under active development.

<a href="https://www.buymeacoffee.com/niceboygithub" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
