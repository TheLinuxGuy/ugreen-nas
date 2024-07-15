# Proxmox LED installation

My TL;DR installation instructions to get https://github.com/miskcoo/ugreen_dx4600_leds_controller#start-at-boot-for-debian-12 installed.

## Maintenance tasks

New disks added/removed/leds stuck. 
```
lsblk -S -x hctl -o name,hctl,serial
systemctl restart ugreen-diskiomon
```

## Installation steps

1. Modify `/etc/apt/sources.list` and `non-free`

```
deb http://deb.debian.org/debian bookworm main contrib non-free
```

2. Run `apt-get update` 

3. Attempt install `apt-get install dkms git i2c-tools` you may get an error, if so try `apt --fix-broken install`.

4. Install PVE headers. `apt install pve-headers-$(uname -r)`
5. Download .deb package from github and into a folder on the server. Attempt to install `dpkg -i led-ugreen-dkms_0.1_amd64.deb `

6. Download source scripts `git clone https://github.com/miskcoo/ugreen_dx4600_leds_controller.git`

7. Execute `modprobe -v i2c-dev`

8. Execute script within folder and verify LEDs are seen.

```
# sh /root/unas/ugreen_dx4600_leds_controller/scripts/ugreen-probe-leds 
Found I2C device /dev/i2c-0
```

9. Create the systemd configuration; pick the eth# to monitor and enable the service to start at boot if all goes well.

```
root@UNO:~/unas/ugreen_dx4600_leds_controller/scripts# ls
ugreen-diskiomon	  ugreen-leds.conf  ugreen-netdevmon@.service
ugreen-diskiomon.service  ugreen-netdevmon  ugreen-probe-leds
root@UNO:~/unas/ugreen_dx4600_leds_controller/scripts# for f in ${scripts[@]}; do
    chmod +x "scripts/$f"
    cp "scripts/$f" /usr/bin
done
root@UNO:~/unas/ugreen_dx4600_leds_controller/scripts# cp scripts/ugreen-leds.conf /etc/ugreen-leds.conf
cp: cannot stat 'scripts/ugreen-leds.conf': No such file or directory
root@UNO:~/unas/ugreen_dx4600_leds_controller/scripts# cp ugreen-leds.conf /etc/ugreen-leds.conf
root@UNO:~/unas/ugreen_dx4600_leds_controller/scripts# cp *.service /etc/systemd/system/
root@UNO:~/unas/ugreen_dx4600_leds_controller/scripts# systemctl daemon-reload
root@UNO:~/unas/ugreen_dx4600_leds_controller/scripts# systemctl start ugreen-netdevmon@enp88s0
root@UNO:~/unas/ugreen_dx4600_leds_controller/scripts# systemctl start ugreen-diskiomon
root@UNO:~/unas/ugreen_dx4600_leds_controller/scripts# systemctl enable ugreen-diskiomon
Created symlink /etc/systemd/system/multi-user.target.wants/ugreen-diskiomon.service → /etc/systemd/system/ugreen-diskiomon.service.
root@UNO:~/unas/ugreen_dx4600_leds_controller/scripts# systemctl enable ugreen-netdevmon@enp88s0
Created symlink /etc/systemd/system/multi-user.target.wants/ugreen-netdevmon@enp88s0.service → /etc/systemd/system/ugreen-netdevmon@.service.

```
The network LED should now be blinking if there's network activity. The software is installed on proxmox; you can configure disk LEDs.

### Disk mapping to LEDs

I won't repeat the content from https://github.com/miskcoo/ugreen_dx4600_leds_controller?tab=readme-ov-file#disk-mapping simply dump the list of commands that are specific to my setup but this should be enough for you to get the idea.

**DXP6800 Pro has special mappings.** `0:0:0:0 and 1:0:0:0 are mapped to disk5 and disk6, and 2:0:0:0 to 6:0:0:0 are mapped to disk1 to disk4`

1. `lsblk -S -x hctl -o name,hctl,serial` Displays current diskinfo.

2. edit or create `/etc/modules-load.d/ugreen-led.conf`

```
i2c-dev
led-ugreen
ledtrig-oneshot
ledtrig-netdev
```

3. Edit configuration with DXP6800 Pro settings.

```
CHECK_GATEWAY_CONNECTIVITY=true
CHECK_LINK_SPEED=true
```

4. If we installed the dkms in the lazy way via .deb package. The file `/usr/bin/ugreen-diskiomon` is out of date, let's wipe it out with one that works and is modified by me to have the DXP6800 Pro special map pre-configred.

`/usr/bin/ugreen-diskiomon` DXP6800 Pro settings to override.
```
hctl_map=("2:0:0:0" "3:0:0:0" "4:0:0:0" "5:0:0:0" "0:0:0:0" "1:0:0:0")
ata_map=("ata3" "ata4" "ata5" "ata6" "ata1" "ata2")
```