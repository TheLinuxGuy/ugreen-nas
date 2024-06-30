# ugreen-nas
My public notes, findings and experience with UGREEN DXP6800 Pro NAS from kickstarter

## PCI Express lanes and bandwidth

My DXP6800 has multiple NVME slots; not all of them run at full speeds (x4), not all of them are PCIe 4.0. Information on reddit about the details of them is limited - so I spent a weekend tinkering to answer this question in detail.

TL;DR
- UGOS nvme slot (base operating system, not easily accessible, requires tear down): **PCIe 3.0 x1 ~800 MB/s)**
- NVME slot 1: **PCIE 3.0 x4 ~3500 MB/s**
- NVME slot 2: **PCIE 4.0 x4 ~7000 MB/s**

The DXP6800 Pro has a PCIE 4.0 expansion slot and using an nvme PCIE bracket I was able to get **4 NVME devices on the DXP6800** operating at the same time. 

Due to PCIE bandwidth limitations the experience is not equal among the nvme devices - thus a RAID NVME array would suffer from performance bottlenecks on its weakest link PCIE 3.0 x1

### UGREEN OS "CACHE" techniques and setup

UGREEN uses lvmcache in `cache` mode with `mq` algorithm. They put mdraid on top of it all - btrfs filesystem is used on the LV.

### How does UGREEN OS compare to Synology DSM?

UGREEN is barebones compared to my synology. It will do the basics of btrfs storage and caching - the most major drawback is UGREEN hasn't implemented a btrfs snapshot (ability to "undelete" files, in Synology this is managed via `Snapshot Replication` app).

If all you are looking for in a NAS is throwing a bunch of disks on a RAID with a decent catching that's better than synology (which is a hotspot cache only). UGREEN can probably fit the bill if you're willing to risk or lack the ability to restore files edited a few hours/days ago from a data snapshot of the filesystem.

## Entering the BIOS and Boot Menu 

`CONTROL + F12` to get menu to select which disk to boot.

`CONTROL + F2` to get to BIOS. If running third party OS, disable watchdog service.

## Backing up and restoring the original UGREEN OS

I have successfully backed up the 128gb NVME included with the DXP6800 Pro into a 1TB NVME using Clonezilla. As of Jun 30, 2024 UGREEN does not provide a bootable USB or ISO to install their operating system into any disk.

## Third party OS on DXP6800 Pro and those disk activity LEDs

Proxmox and many other OS will run fine on this device. For the disk activity LED's you will need to use: https://github.com/miskcoo/ugreen_dx4600_leds_controller