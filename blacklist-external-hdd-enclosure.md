# Blacklisting external USB3 3.5" SATA enclosure

```bash
root@MS1:~# cat /etc/udev/rules.d/99-ignore-usb-device.rules
SUBSYSTEM=="usb", ATTR{idVendor}=="2109", ATTR{idProduct}=="0822", ATTR{authorized}="0"
SUBSYSTEM=="usb", ATTR{idVendor}=="174c", ATTR{idProduct}=="55aa", ATTR{authorized}="0"
SUBSYSTEM=="usb", ATTR{idVendor}=="2109", ATTR{idProduct}=="2822", ATTR{authorized}="0"
root@MS1:~#
```

`udevadm control --reload-rules`

2024-09-29T16:19:36:INFO:Unmanic.PostProcessor - [FORMATTED] - Removing remote source: /tmp/unmanic/remote_library/unmanic_remote_pending_library-1727641167.02471/S01E02 - Deep Throat Bluray-720p.mkv

