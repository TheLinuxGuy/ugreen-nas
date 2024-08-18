# TheLinuxGuy FlexRAID experiments

Goals
- NAS with different sized disks (8TB, 10TB, 14TB, 18TB)
- Do not waste space. Use partitions rather than whole disks, aka manual RAID planning. Try to mimic Synology SHR benefits.
- Must survive 1 disk failure

Resources
- https://documentation.suse.com/sles/12-SP5/html/SLES-all/cha-raid-resize.html
- https://niziak.spox.org/wiki/linux:fs:zfs:shrink

### Update 08/17/2024

Some guy on OpenMediaVault just shared this week a more detailed post on how to do `sliced hybrid raid (SHR)` - take a look at his post as I tend to keep my notes on github to the bare essentials / TL;DR... 

If you want to read about why XYZ I made, refer to his post for it.
https://forum.openmediavault.org/index.php?thread/53652-howto-build-an-shr-sliced-hybrid-raid/&postID=398248#post398248

## Upgrade pair of 8TB to 14TB disks

State
- bcache backing storage is LVM2
- All physical disks are members of mdadm raid.
- Two 8TB are members of /dev/md126
- Remove one 8TB disk and replace with 14TB disks
- Minimum partition size across mdadm set is 8TB (original setup).

Expected steps
- 14TB needs to be partitioned




### Starting point configuration dump

```bash
root@UNO:~# mdadm --detail /dev/md12[56]
/dev/md125:
           Version : 1.2
     Creation Time : Sun Jul 28 04:41:27 2024
        Raid Level : raid1
        Array Size : 1952378880 (1861.93 GiB 1999.24 GB)
     Used Dev Size : 1952378880 (1861.93 GiB 1999.24 GB)
      Raid Devices : 2
     Total Devices : 2
       Persistence : Superblock is persistent

     Intent Bitmap : Internal

       Update Time : Wed Jul 31 21:54:01 2024
             State : clean
    Active Devices : 2
   Working Devices : 2
    Failed Devices : 0
     Spare Devices : 0

Consistency Policy : bitmap

              Name : UNO:1  (local to host UNO)
              UUID : afe875ad:cb818bc7:26288ce2:33d52b1d
            Events : 3566

    Number   Major   Minor   RaidDevice State
       0       8       50        0      active sync   /dev/sdd2
       1       8       34        1      active sync   /dev/sdc2
/dev/md126:
           Version : 1.2
     Creation Time : Sun Jul 28 04:31:18 2024
        Raid Level : raid5
        Array Size : 23441372160 (21.83 TiB 24.00 TB)
     Used Dev Size : 7813790720 (7.28 TiB 8.00 TB)
      Raid Devices : 4
     Total Devices : 4
       Persistence : Superblock is persistent

     Intent Bitmap : Internal

       Update Time : Wed Jul 31 21:54:11 2024
             State : clean
    Active Devices : 4
   Working Devices : 4
    Failed Devices : 0
     Spare Devices : 0

            Layout : left-symmetric
        Chunk Size : 512K

Consistency Policy : bitmap

              Name : UNO:0  (local to host UNO)
              UUID : 26f6d390:55236ad7:e1457b27:cbe5318f
            Events : 14913

    Number   Major   Minor   RaidDevice State
       0       8       65        0      active sync   /dev/sde1
       1       8       81        1      active sync   /dev/sdf1
       2       8       49        2      active sync   /dev/sdd1
       4       8       33        3      active sync   /dev/sdc1
root@UNO:~# lsscsi
[0:0:0:0]    disk    ATA      T-FORCE 2TB      7A0   /dev/sda
[1:0:0:0]    disk    ATA      WDC WD180EDGZ-11 0A85  /dev/sdb
[2:0:0:0]    disk    ATA      WDC WD100EMAZ-00 0A83  /dev/sdc
[3:0:0:0]    disk    ATA      WDC WD100EMAZ-00 0A83  /dev/sdd
[4:0:0:0]    disk    ATA      WDC WD80EFAX-68L 0A83  /dev/sde
[5:0:0:0]    disk    ATA      WDC WD80EFZX-68U 0A83  /dev/sdf
[6:0:0:0]    cd/dvd  PiKVM    CD-ROM Drive     0606  /dev/sr0
[N:0:8215:1] disk    WD Red SN700 1000GB__1                     /dev/nvme0n1
[N:1:1:1]    disk    YSO128GTLCW-E3C-2__1                       /dev/nvme1n1
[N:2:4:1]    disk    Samsung SSD 970 EVO Plus 1TB__1            /dev/nvme2n1
root@UNO:~#
root@UNO:~# bcache-super-show /dev/mapper/vg1-slowsky
sb.magic		ok
sb.first_sector		8 [match]
sb.csum			1C98D664FAF1558F [match]
sb.version		1 [backing device]

dev.label		(empty)
dev.uuid		23925344-524a-4a05-a192-1cd98001e2d4
dev.sectors_per_block	8
dev.sectors_per_bucket	4096
dev.data.first_sector	16
dev.data.cache_mode	1 [writeback]
dev.data.cache_state	1 [clean]

cset.uuid		3583a096-8787-4aa6-9443-1a8173457885
root@UNO:~# pvdisplay
  --- Physical volume ---
  PV Name               /dev/md126
  VG Name               vg1
  PV Size               21.83 TiB / not usable 5.00 MiB
  Allocatable           yes (but full)
  PE Size               4.00 MiB
  Total PE              5722990
  Free PE               0
  Allocated PE          5722990
  PV UUID               KbNfP3-1839-MTJx-Z50O-qTow-1lpt-ZmvkCa

  --- Physical volume ---
  PV Name               /dev/md125
  VG Name               vg1
  PV Size               <1.82 TiB / not usable 4.00 MiB
  Allocatable           yes (but full)
  PE Size               4.00 MiB
  Total PE              476654
  Free PE               0
  Allocated PE          476654
  PV UUID               sbY6za-2RKI-0KVO-c7Zc-MmKD-4o6U-x6hw1R

  --- Physical volume ---
  PV Name               /dev/sda
  VG Name               vg1
  PV Size               1.86 TiB / not usable <2.34 MiB
  Allocatable           yes
  PE Size               4.00 MiB
  Total PE              488378
  Free PE               24419
  Allocated PE          463959
  PV UUID               N1kAU3-9pJV-TXfl-G2s9-iXWB-Q3dF-CXZbR7
```