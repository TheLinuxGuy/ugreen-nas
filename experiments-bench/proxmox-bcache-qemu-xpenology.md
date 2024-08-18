# You're absolutely crazy and don't care about your data experiment.

Goals:
- Proxmox base OS deals with all direct-attached storage disks
- hd-idle on proxmox to lower power consumption on slow hdds.
- bcache because we want hybrid storage NVME+HDD.
- writeback cache setup, mdadm raid 1TB nvme disks block storage.

### Assumptions / what are we doing here?

- We want a RAID5 array that gives us close to NVME speed on HDDs for rarely read media files (1GB>) for plex server.
- We don't want to have to deal with `mover` type scripts from https://github.com/TheLinuxGuy/free-unraid
- Speed, some parity guarantees are needed.
- Want a simple web UI and management, this is delivered thanks to xpenology / vDSM.

#### bcache special paths to remember

`/sys/block/sdc/bcache/stop`
`echo 1 > /sys/block/md127/md127p1/bcache/set/stop`

#### Setup

Remember DXP6800 Pro first and second disks are actually 5,6 slots. 

```
root@UNO:~# lsscsi
[0:0:0:0]    disk    ATA      WDC WD140EDFZ-11 0A81  /dev/sda
[1:0:0:0]    disk    ATA      WDC WD80EFZX-68U 0A83  /dev/sdb
[2:0:0:0]    disk    ATA      WDC WD100EMAZ-00 0A83  /dev/sdc
[3:0:0:0]    disk    ATA      WDC WD100EMAZ-00 0A83  /dev/sdd
[4:0:0:0]    disk    ATA      WDC WD140EDFZ-11 0A81  /dev/sde
[5:0:0:0]    disk    ATA      WDC WD180EDGZ-11 0A85  /dev/sdf
[N:0:4:1]    disk    Samsung SSD 970 EVO Plus 1TB__1            /dev/nvme0n1
[N:1:8215:1] disk    WD Red SN700 1000GB__1                     /dev/nvme1n1
[N:2:1:1]    disk    YSO128GTLCW-E3C-2__1                       /dev/nvme2n1
root@UNO:~#
```

Let's start bcache0 from physical bay 1...

```bash
root@UNO:/# make-bcache -B /dev/sdc /dev/sdd /dev/sde /dev/sdf /dev/sda /dev/sdb -C /dev/md127p1 --block 4k --bucket 2M --writeback --wipe-bcacheUUID:			b6bbb7f0-20b6-4a9a-8e57-854cffccc27a
Set UUID:		04a99c31-edd0-4d74-8ac4-a7eec9ef8533
version:		0
nbuckets:		419430
block_size:		8
bucket_size:		4096
nr_in_set:		1
nr_this_dev:		0
first_bucket:		1
UUID:			e0969f10-6ee8-4a9a-a2c3-8cc22e6515d5
Set UUID:		04a99c31-edd0-4d74-8ac4-a7eec9ef8533
version:		1
block_size:		8
data_offset:		16
UUID:			1568dc32-50f7-437b-a2ac-60539ab172b3
Set UUID:		04a99c31-edd0-4d74-8ac4-a7eec9ef8533
version:		1
block_size:		8
data_offset:		16
UUID:			bfd3c739-0d74-4174-973d-a38f1381be03
Set UUID:		04a99c31-edd0-4d74-8ac4-a7eec9ef8533
version:		1
block_size:		8
data_offset:		16
UUID:			4c2a5bfe-c8f7-4938-a579-d73007a6bf3e
Set UUID:		04a99c31-edd0-4d74-8ac4-a7eec9ef8533
version:		1
block_size:		8
data_offset:		16
UUID:			e2dbd79d-bf14-4dd7-8933-3adcf35ad28e
Set UUID:		04a99c31-edd0-4d74-8ac4-a7eec9ef8533
version:		1
block_size:		8
data_offset:		16
UUID:			a2623a6d-dcc7-4ecb-b52c-7054bd6c3273
Set UUID:		04a99c31-edd0-4d74-8ac4-a7eec9ef8533
version:		1
block_size:		8
data_offset:		16
```

Speed freak tweaks

```bash
cachecset=04a99c31-edd0-4d74-8ac4-a7eec9ef8533
echo 0 > /sys/fs/bcache/$cachecset/congested_write_threshold_us 
echo 0 > /sys/fs/bcache/$cachecset/congested_read_threshold_us 
for i in {0..5}; do echo bcache$i; echo 0 >/sys/block/bcache$i/bcache/sequential_cutoff ; done
for i in {0..5}; do echo bcache$i; echo 8192 > /sys/block/bcache$i/queue/read_ahead_kb ; done
for i in {0..5}; do echo bcache$i; echo 10 > /sys/class/block/bcache$i/bcache/writeback_delay ; done
```

#### XPE

Import ARC loader disk file to pre-creared VM.
`qm disk import 132 arc.img local-zfs`

Go attach the disk IDE:0 , enable `writeback`

Let's attach the bcache disks now.

```bash
root@UNO:~# qm set 132 -scsi0 /dev/bcache0
update VM 132: -scsi0 /dev/bcache0
root@UNO:~# qm set 132 -scsi1 /dev/bcache1
update VM 132: -scsi1 /dev/bcache1
root@UNO:~# qm set 132 -scsi2 /dev/bcache2
update VM 132: -scsi2 /dev/bcache2
root@UNO:~# qm set 132 -scsi3 /dev/bcache3
update VM 132: -scsi3 /dev/bcache3
root@UNO:~# qm set 132 -scsi4 /dev/bcache4
update VM 132: -scsi4 /dev/bcache4
root@UNO:~# qm set 132 -scsi5 /dev/bcache5
update VM 132: -scsi5 /dev/bcache5
```

Writeback rate minimum

```bash
find /sys/ -type f -name "congested_write_threshold_us" -path "*/bcache/*"  -exec bash -c 'echo 0 > {}' \;
find /sys/ -type f -name "congested_read_threshold_us" -path "*/bcache/*"  -exec bash -c 'echo 0 > {}' \;
find /sys/ -type f -name "writeback_delay" -path "*/bcache/*" -exec bash -c 'echo 10 > {}' \;
find /sys/ -type f -name "writeback_rate_minimum" -path "*/bcache/*" -exec bash -c 'echo 4096 > {}' \;
find /sys/ -type f -name "writeback_percent" -path "*/bcache/*" -exec bash -c 'echo 1 > {}' \;
find /sys/ -type f -name "read_ahead_kb" -path "*/bcache*/queue/*" -exec bash -c 'echo 8192 > {}' \;
```

Debug and how dirty which disk.
```bash
find /sys/ -type f -name "writeback_rate_debug" -path "*/bcache/*"  -exec bash -c 'echo {} ; cat {}' \;
```

#### bcache nvme discard

The /dev/md127 RAID1 1TB nvme is partitioned intentionally with a dummy partition ~15% of disk that we use for garbage collection.

This command will trigger the nvme to shift data blocks and improve speeds. We don't need `fstrim`

`blkdiscard /dev/md127p2`

#### Remove / wipe old backing storage

 Remove `/dev/sdc` via `echo 1 > /sys/block/sdc/bcache/stop` otherwise system will complain disk is use, and `lsof` `fuser` and other commands will never find a process id that has a lock since its bcache kernel lock and not a process.