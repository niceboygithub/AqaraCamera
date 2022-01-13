# Aqara Camera G3 integration for Home Assistant

**ATTENTION:** The component **only works after enabled telnet.** Only supportd stream. Not support motion detection, ai etc. yet.

This is a way to [enable telnet](https://github.com/Wh1terat/aQRootG3) from #Wh1terat. Thankes for Wh1terat for the amazing aQRootG3 v0.2.0.

After enabled telnet, you need to finish the configuration before reboot G3.


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

```
ffmpeg:
```
## WebRTC

You can use [@AlexxIT's WebRTC](https://github.com/AlexxIT/WebRTC) integration. The usage was well documented in AlexxIT's github.
The rtsp url can be found in Attributes of Camera (find it in developer-tools/state).
You need to notice that the url was changed on every reboot of Aqara Camera.

```
type: custom:webrtc-camera
url: rtsp://66:88@192.168.1.168:8554/720p
ptz:
  service: aqara_camera.ptz
  data_left:
    entity_id: camera.camera_hub_g3_1234
    direction: left
  data_right:
    entity_id: camera.camera_hub_g3_1234
    direction: right
  data_up:
    entity_id: camera.camera_hub_g3_1234
    direction: up
  data_down:
    entity_id: camera.camera_hub_g3_1234
    direction: down
```

Supported Versions
---------------

| Market | Firmware Version | Status |
| -------| --------------- | -- |
| China  | 3.3.2_0019.0004 | :white_check_mark: |
| China  | 3.3.4_0007.0004  | :white_check_mark: |


**Attention:** The component is under active development.

<a href="https://www.buymeacoffee.com/niceboygithub" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
