# Baseline information (to cache or not)

## Slow disks
### mdadm RAID5 (3 disks) raw bcache with backing storage only.

440Mb/s

```
root@UNO:~# pv /dev/bcache0 > /dev/null
12.6GiB 0:00:50 [ 439MiB/s] [>                                                                                               ]  0% ETA 1:00:32:39
14.4GiB 0:00:54 [ 466MiB/s] [>                                                                                                 ]  0% ETA 23:17:33
22.3GiB 0:01:11 [ 449MiB/s] [>                                                                                                 ]  0% ETA 19:45:11
24.8GiB 0:01:16 [ 418MiB/s] [>                                                                                                 ]  0% ETA 19:02:35
^C.2GiB 0:01:17 [ 429MiB/s] [>                                                                                                 ]  0% ETA 18:58:12
root@UNO:~#
```


## NVME cache

### mdadm 

#### btrfs on /dev/md3

```bash
root@UNO:~# mkfs.btrfs -L array -f /dev/md3
root@UNO:~# mount /dev/md3 /mnt/btrfs/
root@UNO:~# ./disk-speedtest.sh /mnt/btrfs/
SEQUENTIAL WRITE: bw=1429MiB/s (1498MB/s), 1429MiB/s-1429MiB/s (1498MB/s-1498MB/s), io=83.9GiB (90.1GB), run=60135-60135msec

RANDOM WRITE: bw=314MiB/s (330MB/s), 314MiB/s-314MiB/s (330MB/s-330MB/s), io=18.4GiB (19.8GB), run=60001-60001msec

SEQUENTIAL READ: bw=6366MiB/s (6676MB/s), 6366MiB/s-6366MiB/s (6676MB/s-6676MB/s), io=373GiB (401GB), run=60053-60053msec

RANDOM READ: bw=993MiB/s (1041MB/s), 993MiB/s-993MiB/s (1041MB/s-1041MB/s), io=58.2GiB (62.5GB), run=60001-60001msec
```

#### ext4 on /dev/md3

SEQUENTIAL WRITE: bw=1787MiB/s
RANDOM WRITE: bw=782MiB/s
SEQUENTIAL READ: bw=6028MiB/s 
RANDOM READ: bw=1425MiB/s 

```bash
root@UNO:~# mkfs.btrfs -L array -f /dev/md3
root@UNO:~# mount /dev/md3 /mnt/btrfs/
root@UNO:~# ./disk-speedtest.sh /mnt/btrfs/
SEQUENTIAL WRITE: bw=1787MiB/s (1874MB/s), 1787MiB/s-1787MiB/s (1874MB/s-1874MB/s), io=105GiB (113GB), run=60108-60108msec

Disk stats (read/write):
    md3: ios=0/227535, merge=0/0, ticks=0/21838730, in_queue=21838730, util=99.86%, aggrios=0/227630, aggrmerge=0/326, aggrticks=0/16096824, aggrin_queue=16097944, aggrutil=99.80%
  nvme0n1: ios=0/227630, merge=0/326, ticks=0/21225500, in_queue=21226799, util=99.80%
  nvme1n1: ios=0/227630, merge=0/326, ticks=0/10968149, in_queue=10969090, util=61.87%
write_iops: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=64

RANDOM WRITE: bw=782MiB/s (820MB/s), 782MiB/s-782MiB/s (820MB/s-820MB/s), io=45.8GiB (49.2GB), run=60001-60001msec

Disk stats (read/write):
    md3: ios=0/12351927, merge=0/0, ticks=0/142545, in_queue=142545, util=99.90%, aggrios=0/12402481, aggrmerge=0/188, aggrticks=0/145241, aggrin_queue=145373, aggrutil=99.57%
  nvme0n1: ios=0/12402481, merge=0/188, ticks=0/162564, in_queue=162713, util=99.57%
  nvme1n1: ios=0/12402481, merge=0/188, ticks=0/127919, in_queue=128033, util=99.54%
read_throughput: (g=0): rw=read, bs=(R) 1024KiB-1024KiB, (W) 1024KiB-1024KiB, (T) 1024KiB-1024KiB, ioengine=libaio, iodepth=64

SEQUENTIAL READ: bw=6028MiB/s (6321MB/s), 6028MiB/s-6028MiB/s (6321MB/s-6321MB/s), io=354GiB (380GB), run=60054-60054msec

Disk stats (read/write):
    md3: ios=749938/1735, merge=0/0, ticks=31241649/103140, in_queue=31344789, util=99.94%, aggrios=297563/1753, aggrmerge=77654/28, aggrticks=12148083/30217, aggrin_queue=12180689, aggrutil=99.86%
  nvme0n1: ios=403083/1755, merge=0/26, ticks=15652478/4480, in_queue=15660398, util=99.85%
  nvme1n1: ios=192043/1751, merge=155308/30, ticks=8643688/55955, in_queue=8700981, util=99.86%
read_iops: (g=0): rw=randread, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=64

RANDOM READ: bw=1425MiB/s (1494MB/s), 1425MiB/s-1425MiB/s (1494MB/s-1494MB/s), io=83.5GiB (89.7GB), run=60001-60001msec
Disk stats (read/write):
    md3: ios=22518367/3466, merge=0/0, ticks=1712465/773, in_queue=1713238, util=99.92%, aggrios=11305270/3508, aggrmerge=0/41, aggrticks=856498/1583, aggrin_queue=858153, aggrutil=99.85%
  nvme0n1: ios=8761746/3508, merge=0/41, ticks=884000/1542, in_queue=885614, util=99.85%
  nvme1n1: ios=13848795/3508, merge=0/41, ticks=828996/1625, in_queue=830693, util=99.85%
```


#### zfs on /dev/md3

compared to native zfs raid. Neglible speed differences (100MiB/s) on first 3 but same random read.

```bash
zpool create -o ashift=13 -O atime=off -O compression=lz4 pool /dev/md3

SEQUENTIAL WRITE: bw=1541MiB/s (1616MB/s), 1541MiB/s-1541MiB/s (1616MB/s-1616MB/s), io=90.6GiB (97.3GB), run=60242-60242msec

RANDOM WRITE: bw=1193MiB/s (1251MB/s), 1193MiB/s-1193MiB/s (1251MB/s-1251MB/s), io=69.9GiB (75.0GB), run=60001-60001msec

SEQUENTIAL READ: bw=9473MiB/s (9933MB/s), 9473MiB/s-9473MiB/s (9933MB/s-9933MB/s), io=555GiB (596GB), run=60001-60001msec

RANDOM READ: bw=354MiB/s (371MB/s), 354MiB/s-354MiB/s (371MB/s-371MB/s), io=20.7GiB (22.2GB), run=60001-60001msec
```

### zfs native raid

Slightly faster native speeds but negligible. `ashift=13` is preferred.

```bash
mdadm --stop /dev/md3
zpool create -f  -o ashift=13 -O atime=off -O compression=lz4 pool mirror /dev/nvme1n1 /dev/nvme0n1

SEQUENTIAL WRITE: bw=1648MiB/s (1728MB/s), 1648MiB/s-1648MiB/s (1728MB/s-1728MB/s), io=96.8GiB (104GB), run=60121-60121msec

RANDOM WRITE: bw=1204MiB/s (1263MB/s), 1204MiB/s-1204MiB/s (1263MB/s-1263MB/s), io=70.6GiB (75.8GB), run=60001-60001msec

SEQUENTIAL READ: bw=9536MiB/s (9999MB/s), 9536MiB/s-9536MiB/s (9999MB/s-9999MB/s), io=559GiB (600GB), run=60001-60001msec

RANDOM READ: bw=366MiB/s (383MB/s), 366MiB/s-366MiB/s (383MB/s-383MB/s), io=21.4GiB (23.0GB), run=60001-60001msec

ashift=12 attempt.

SEQUENTIAL WRITE: bw=1625MiB/s (1704MB/s), 1625MiB/s-1625MiB/s (1704MB/s-1704MB/s), io=95.4GiB (102GB), run=60082-60082msec

RANDOM WRITE: bw=1204MiB/s (1262MB/s), 1204MiB/s-1204MiB/s (1262MB/s-1262MB/s), io=70.5GiB (75.7GB), run=60001-60001msec

SEQUENTIAL READ: bw=9574MiB/s (10.0GB/s), 9574MiB/s-9574MiB/s (10.0GB/s-10.0GB/s), io=561GiB (602GB), run=60001-60001msec

RANDOM READ: bw=351MiB/s (368MB/s), 351MiB/s-351MiB/s (368MB/s-368MB/s), io=20.5GiB (22.1GB), run=60001-60001msec
```


### btrfs native raid

compared to mdadm + btrfs:
- faster seq write
- same random write
- slower random reads
- slower sequential reads

```bash
# mkfs.btrfs -f -d single -m raid1  /dev/nvme1n1 /dev/nvme0n1
SEQUENTIAL WRITE: bw=2834MiB/s (2972MB/s), 2834MiB/s-2834MiB/s (2972MB/s-2972MB/s), io=166GiB (178GB), run=60045-60045msec
write_iops: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=64

RANDOM WRITE: bw=343MiB/s (359MB/s), 343MiB/s-343MiB/s (359MB/s-359MB/s), io=20.1GiB (21.6GB), run=60001-60001msec
read_throughput: (g=0): rw=read, bs=(R) 1024KiB-1024KiB, (W) 1024KiB-1024KiB, (T) 1024KiB-1024KiB, ioengine=libaio, iodepth=64

SEQUENTIAL READ: bw=3274MiB/s (3433MB/s), 3274MiB/s-3274MiB/s (3433MB/s-3433MB/s), io=192GiB (206GB), run=60076-60076msec
read_iops: (g=0): rw=randread, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=64

RANDOM READ: bw=1178MiB/s (1235MB/s), 1178MiB/s-1178MiB/s (1235MB/s-1235MB/s), io=69.0GiB (74.1GB), run=60001-60001msec
```