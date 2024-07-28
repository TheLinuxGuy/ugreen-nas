# UGREEN NASync OS - UGOS caching type

Dump all the settings that UGOS seems to use for `writeback` cache, see if we can reproduce the same settings on proxmox later and tweak the performance.

```
lvcreate --type cache --cachevol --cachemode writeback -n array_cpool --cachepolicy mq --cachesettings 'migration_threshold=8192 random_threshold=0 sequential_threshold=0 discard_promote_adjustment=0 read_promote_adjustment=0 write_promote_adjustment=0' vg1/array /dev/md0
```

```bash
root@UNAS:~# lvdisplay
  --- Logical volume ---
  LV Path                /dev/ug_0D1049_1722150692_pool1/volume1
  LV Name                volume1
  VG Name                ug_0D1049_1722150692_pool1
  LV UUID                3GMa60-6PCW-rNKC-KwO8-fjYX-anPc-N51KF7
  LV Write Access        read/write
  LV Creation host, time UNAS, 2024-07-28 03:11:32 -0400
  LV Cache pool name     volume1_lvmcache_cvol
  LV Cache origin name   volume1_corig
  LV Status              available
  # open                 1
  LV Size                14.52 TiB
  Cache used blocks      0.00%
  Cache metadata blocks  16.92%
  Cache dirty blocks     0.00%
  Cache read hits/misses 0 / 0
  Cache wrt hits/misses  0 / 0
  Cache demotions        0
  Cache promotions       0
  Current LE             3807488
  Segments               1
  Allocation             inherit
  Read ahead sectors     auto
  - currently set to     4096
  Block device           253:0

root@UNAS:~# lvs -a -o +devices
  LV                      VG                         Attr       LSize   Pool                    Origin          Data%  Meta%  Move Log Cpy%Sync Convert Devices         
  volume1                 ug_0D1049_1722150692_pool1 Cwi-aoC---  14.52t [volume1_lvmcache_cvol] [volume1_corig] 0.00   16.92           0.00             volume1_corig(0)
  [volume1_corig]         ug_0D1049_1722150692_pool1 owi-aoC---  14.52t                                                                                 /dev/md1(0)     
  [volume1_lvmcache_cvol] ug_0D1049_1722150692_pool1 Cwi-aoC--- 800.00g                                                                                 /dev/md2(0)     
root@UNAS:~# 
root@UNAS:~# lvs -o name,cache_policy,cache_settings ug_0D1049_1722150692_pool1
  LV      CachePolicy CacheSettings
  volume1 smq   

root@UNAS:~# lvs -o name,cache_policy,kernel_cache_settings
  LV      CachePolicy KCacheSettings                                                                                                                                      
  volume1 smq         migration_threshold=8192,random_threshold=0,sequential_threshold=0,discard_promote_adjustment=0,read_promote_adjustment=0,write_promote_adjustment=0  
  ```

  ## dmsetup

  ```bash
  root@UNAS:~# dmsetup ls
ug_0D1049_1722150692_pool1-volume1	(253:0)
ug_0D1049_1722150692_pool1-volume1_corig	(253:4)
ug_0D1049_1722150692_pool1-volume1_lvmcache_cvol	(253:1)
ug_0D1049_1722150692_pool1-volume1_lvmcache_cvol-cdata	(253:2)
ug_0D1049_1722150692_pool1-volume1_lvmcache_cvol-cmeta	(253:3)
root@UNAS:~# dm info ug_0D1049_1722150692_pool1-volume1
-sh: dm: not found
root@UNAS:~# dmsetup info ug_0D1049_1722150692_pool1-volume1
Name:              ug_0D1049_1722150692_pool1-volume1
State:             ACTIVE
Read Ahead:        4096
Tables present:    LIVE
Open count:        1
Event number:      1
Major, minor:      253, 0
Number of targets: 1
UUID: LVM-qtkWTzF85FmNCFoRh1NT8CviSwOVAAZm3GMa606PCWrNKCKwO8fjYXanPcN51KF7

root@UNAS:~# dmsetup info ug_0D1049_1722150692_pool1-volume1_lvmcache_cvol
Name:              ug_0D1049_1722150692_pool1-volume1_lvmcache_cvol
State:             ACTIVE
Read Ahead:        256
Tables present:    LIVE
Open count:        2
Event number:      0
Major, minor:      253, 1
Number of targets: 1
UUID: LVM-qtkWTzF85FmNCFoRh1NT8CviSwOVAAZmpu9IERiiGzdyx8Dnx3k0pEYNmxPo7Jgc-cvol

root@UNAS:~# dmsetup status
ug_0D1049_1722150692_pool1-volume1: 0 31190941696 cache 8 4910/19456 1024 7639/1638248 10967540 2035 39818 893 0 7639 0 3 metadata2 writeback no_discard_passdown 2 migration_threshold 8192 mq 10 random_threshold 0 sequential_threshold 0 discard_promote_adjustment 0 read_promote_adjustment 0 write_promote_adjustment 0 rw - 
ug_0D1049_1722150692_pool1-volume1_corig: 0 31190941696 linear 
ug_0D1049_1722150692_pool1-volume1_lvmcache_cvol: 0 1677721600 linear 
ug_0D1049_1722150692_pool1-volume1_lvmcache_cvol-cdata: 0 1677565952 linear 
ug_0D1049_1722150692_pool1-volume1_lvmcache_cvol-cmeta: 0 155648 linear 
root@UNAS:~# 
root@UNAS:~# dmsetup deps
ug_0D1049_1722150692_pool1-volume1: 3 dependencies	: (253, 4) (253, 2) (253, 3)
ug_0D1049_1722150692_pool1-volume1_corig: 1 dependencies	: (9, 1)
ug_0D1049_1722150692_pool1-volume1_lvmcache_cvol: 1 dependencies	: (9, 2)
ug_0D1049_1722150692_pool1-volume1_lvmcache_cvol-cdata: 1 dependencies	: (253, 1)
ug_0D1049_1722150692_pool1-volume1_lvmcache_cvol-cmeta: 1 dependencies	: (253, 1)
```

#### volumegroup

```bash
root@UNO:~# vgdisplay ug_0D1049_1722150692_pool1
  --- Volume group ---
  VG Name               ug_0D1049_1722150692_pool1
  System ID
  Format                lvm2
  Metadata Areas        2
  Metadata Sequence No  18
  VG Access             read/write
  VG Status             resizable
  MAX LV                0
  Cur LV                0
  Open LV               0
  Max PV                0
  Cur PV                2
  Act PV                2
  VG Size               <15.42 TiB
  PE Size               4.00 MiB
  Total PE              4042093
  Alloc PE / Size       0 / 0
  Free  PE / Size       4042093 / <15.42 TiB
  VG UUID               qtkWTz-F85F-mNCF-oRh1-NT8C-viSw-OVAAZm
```

### lvmcache stats script
https://gist.github.com/love4taylor/632f3148c8920326207ad9f18bdb84b0 

`apt-get install bc`

```bash
root@UNAS:~# ./lvmcache.sh 
-------------------------------------------------------------------------
LVM [2.03.16(2)] cache report of found device /dev/ug_0D1049_1722150692_pool1/volume1
-------------------------------------------------------------------------
- Cache Usage: 0% - Metadata Usage: 16.9%
Runtime error (func=(main), adr=15): Divide by zero
Runtime error (func=(main), adr=15): Divide by zero
- Read Hit Rate: % - Write Hit Rate: %
- Demotions/Promotions/Dirty: 0/0/0
- Feature arguments in use: metadata2 writeback no_discard_passdown 
- Core arguments in use : migration_threshold 8192 mq 10 
  - Cache Policy: multiqueue (mq)
  - Policy arguments in use: 
- Cache Metadata Mode: sequential_threshold
- MetaData Operation Health: needs-check
```

