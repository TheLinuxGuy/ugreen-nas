# ugreen-nas
My public notes, findings and experience with UGREEN DXP6800 Pro NAS from kickstarter

## PCI Express lanes and bandwidth

My DXP6800 has multiple NVME slots; not all of them run at full speeds (x4), not all of them are PCIe 4.0. Information on reddit about the details of them is limited - so I spent a weekend tinkering to answer this question in detail.

TL;DR
- UGOS nvme slot (base operating system, not easily accessible, requires tear down): **PCIe 3.0 x1  ~800 MB/s**
- NVME slot 1: **PCIE 3.0 x2 ~1600 MB/s**
- NVME slot 2 (next to memory slot): **PCIE 3.0 x4 ~3600 MB/s**
- PCIe slot PCIE 3.0 x4.

The DXP6800 Pro has a PCIE 4.0 expansion slot and using an nvme PCIE bracket I was able to get **4 NVME devices on the DXP6800** operating at the same time. 

Due to PCIE bandwidth limitations the experience is not equal among the nvme devices - thus a RAID NVME array would suffer from performance bottlenecks on its weakest link PCIE 3.0 x1

Evidence from my setup

```
# nvme list -v 
Subsystem        Subsystem-NQN                                                                                    Controllers
---------------- ------------------------------------------------------------------------------------------------ ----------------
nvme-subsys3     nqn.2018-01.com.wdc:nguid:E8238FA6BF53-0001-001B448B478C24C8                                     nvme3
nvme-subsys2     nqn.2023-03.com.intel:nvm-subsystem-sn-phka311603lz2p0c                                          nvme2
nvme-subsys1     nqn.2014.08.org.nvmexpress:c0a9c0a92307E6AD9D94        CT2000P3SSD8                              nvme1
nvme-subsys0     nqn.2023-03.com.intel:nvm-subsystem-sn-btka312104k52p0c                                          nvme0

Device   SN                   MN                                       FR       TxPort Address        Subsystem    Namespaces      
-------- -------------------- ---------------------------------------- -------- ------ -------------- ------------ ----------------
nvme3    x         WD Red SN700 1000GB                      111150WD pcie   0000:58:00.0   nvme-subsys3 nvme3n1
nvme2    x     INTEL SSDPEKNU020TZ                      002C     pcie   0000:57:00.0   nvme-subsys2 nvme2n1
nvme1    x         CT2000P3SSD8                             P9CR30A  pcie   0000:02:00.0   nvme-subsys1 nvme1n1
nvme0    x     INTEL SSDPEKNU020TZ                      003C     pcie   0000:01:00.0   nvme-subsys0 nvme0n1

Device       Generic      NSID     Usage                      Format           Controllers     
------------ ------------ -------- -------------------------- ---------------- ----------------
/dev/nvme3n1 /dev/ng3n1   1          1.00  TB /   1.00  TB    512   B +  0 B   nvme3
/dev/nvme2n1 /dev/ng2n1   1          2.05  TB /   2.05  TB    512   B +  0 B   nvme2
/dev/nvme1n1 /dev/ng1n1   1          2.00  TB /   2.00  TB    512   B +  0 B   nvme1
/dev/nvme0n1 /dev/ng0n1   1          2.05  TB /   2.05  TB    512   B +  0 B   nvme0
# lspci -vv -nn -s 0000:58:00.0|grep Lnk
		LnkCap:	Port #0, Speed 8GT/s, Width x4, ASPM L1, Exit Latency L1 <8us
		LnkCtl:	ASPM Disabled; RCB 64 bytes, Disabled- CommClk+
		LnkSta:	Speed 8GT/s, Width x1 (downgraded)
		LnkCap2: Supported Link Speeds: 2.5-8GT/s, Crosslink- Retimer- 2Retimers- DRS-
		LnkCtl2: Target Link Speed: 8GT/s, EnterCompliance- SpeedDis-
		LnkSta2: Current De-emphasis Level: -6dB, EqualizationComplete+ EqualizationPhase1+
		LnkCtl3: LnkEquIntrruptEn- PerformEqu-
# lspci -vv -nn -s 0000:57:00.0|grep Lnk
		LnkCap:	Port #0, Speed 8GT/s, Width x4, ASPM L1, Exit Latency L1 <8us
		LnkCtl:	ASPM Disabled; RCB 64 bytes, Disabled- CommClk+
		LnkSta:	Speed 8GT/s, Width x2 (downgraded)
		LnkCap2: Supported Link Speeds: 2.5-8GT/s, Crosslink- Retimer- 2Retimers- DRS-
		LnkCtl2: Target Link Speed: 8GT/s, EnterCompliance- SpeedDis-
		LnkSta2: Current De-emphasis Level: -6dB, EqualizationComplete+ EqualizationPhase1+
		LnkCtl3: LnkEquIntrruptEn- PerformEqu-
# lspci -vv -nn -s 0000:02:00.0|grep Lnk
		LnkCap:	Port #1, Speed 8GT/s, Width x4, ASPM L1, Exit Latency L1 unlimited
		LnkCtl:	ASPM Disabled; RCB 64 bytes, Disabled- CommClk+
		LnkSta:	Speed 8GT/s, Width x4
		LnkCap2: Supported Link Speeds: 2.5-8GT/s, Crosslink- Retimer- 2Retimers- DRS-
		LnkCtl2: Target Link Speed: 8GT/s, EnterCompliance- SpeedDis-
		LnkSta2: Current De-emphasis Level: -6dB, EqualizationComplete+ EqualizationPhase1+
		LnkCtl3: LnkEquIntrruptEn- PerformEqu-
# lspci -vv -nn -s 0000:01:00.0|grep Lnk
		LnkCap:	Port #0, Speed 8GT/s, Width x4, ASPM L1, Exit Latency L1 <8us
		LnkCtl:	ASPM Disabled; RCB 64 bytes, Disabled- CommClk+
		LnkSta:	Speed 8GT/s, Width x4
		LnkCap2: Supported Link Speeds: 2.5-8GT/s, Crosslink- Retimer- 2Retimers- DRS-
		LnkCtl2: Target Link Speed: 8GT/s, EnterCompliance- SpeedDis-
		LnkSta2: Current De-emphasis Level: -6dB, EqualizationComplete+ EqualizationPhase1+
		LnkCtl3: LnkEquIntrruptEn- PerformEqu-
```

### UGREEN OS "CACHE" techniques and setup

UGREEN uses lvmcache in `cache` mode with `mq` algorithm. They put mdraid on top of it all - btrfs filesystem is used on the LV.

### How does UGREEN OS compare to Synology DSM?

UGREEN is barebones compared to my synology. It will do the basics of btrfs storage and caching - the most major drawback is UGREEN hasn't implemented a btrfs snapshot (ability to "undelete" files, in Synology this is managed via `Snapshot Replication` app).

If all you are looking for in a NAS is throwing a bunch of disks on a RAID with a decent catching that's better than synology (which is a hotspot cache only). UGREEN can probably fit the bill if you're willing to risk or lack the ability to restore files edited a few hours/days ago from a data snapshot of the filesystem.

## Entering the BIOS and Boot Menu 

`CONTROL + F12` to get menu to select which disk to boot.

`CONTROL + F2` to get to BIOS. If running third party OS, disable watchdog service.

`CONTROL + F1` after you are inside BIOS to be able to [view ALL hidden options](https://www.reddit.com/r/UgreenNASync/comments/1e83h8l/trying_to_modify_bios_to_lower_power_consumption/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button).

## Backing up and restoring the original UGREEN OS

I have successfully backed up the 128gb NVME included with the DXP6800 Pro into a 1TB NVME using Clonezilla. As of Jun 30, 2024 UGREEN does not provide a bootable USB or ISO to install their operating system into any disk.

## Third party OS on DXP6800 Pro and those disk activity LEDs

Proxmox and many other OS will run fine on this device. For the disk activity LED's you will need to use: https://github.com/miskcoo/ugreen_dx4600_leds_controller