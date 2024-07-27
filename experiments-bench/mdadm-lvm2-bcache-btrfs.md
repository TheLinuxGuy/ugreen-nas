# mdadm + lvm2 + bcache + btrfs

What is this:
- Add bcache to the mix
- RAID5 mdadm on all physical disks (8TB + 8TB + 10TB + 10TB)
- Use partitions, mimic Synology flexible RAID to use different sized disks
- LVM2 to tie this together via LVs
- btrfs filesystem

### Setup notes

```
:~# wipefs -a /dev/mapper/vg1-array
/dev/mapper/vg1-array: 8 bytes were erased at offset 0x00010040 (btrfs): 5f 42 48 52 66 53 5f 4d
:~# make-bcache -B /dev/mapper/vg1-array
UUID:			0fd31181-c77e-4a6f-ac4e-20afd4177e54
Set UUID:		6a021cfe-eec8-4a66-80ba-8c17d8e930cd
version:		1
block_size:		1
data_offset:		16
:~# make-bcache -C /dev/nvme2n1
UUID:			214d939a-4f74-4710-a967-bd2aca46837a
Set UUID:		bdf9245a-4a7f-4838-a306-f06f243183ff
version:		0
nbuckets:		1907739
block_size:		1
bucket_size:		1024
nr_in_set:		1
nr_this_dev:		0
first_bucket:		1
# echo bdf9245a-4a7f-4838-a306-f06f243183ff > /sys/block/bcache0/bcache/attach
# mkfs.btrfs -L array /dev/bcache0 
btrfs-progs v6.2
See http://btrfs.wiki.kernel.org for more information.

Performing full device TRIM /dev/bcache0 (23.65TiB) ...
NOTE: several default settings have changed in version 5.15, please make sure
      this does not affect your deployments:
      - DUP for metadata (-m dup)
      - enabled no-holes (-O no-holes)
      - enabled free-space-tree (-R free-space-tree)

Label:              array
UUID:               c858171f-34ec-4b3d-9ee0-c13f6fed8979
Node size:          16384
Sector size:        4096
Filesystem size:    23.65TiB
Block group profiles:
  Data:             single            8.00MiB
  Metadata:         DUP               1.00GiB
  System:           DUP               8.00MiB
SSD detected:       yes
Zoned device:       no
Incompat features:  extref, skinny-metadata, no-holes
Runtime features:   free-space-tree
Checksum:           crc32c
Number of devices:  1
Devices:
   ID        SIZE  PATH
    1    23.65TiB  /dev/bcache0

# mount /dev/bcache0 /mnt/btrfs/

```

### Test results

The best results was the proper settings below.

TL;DR
```
SEQUENTIAL WRITE: bw=900MiB/s (943MB/s), 900MiB/s-900MiB/s (943MB/s-943MB/s), io=52.7GiB (56.6GB), run=60029-60029msec
write_iops: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=64

RANDOM WRITE: bw=239MiB/s (251MB/s), 239MiB/s-239MiB/s (251MB/s-251MB/s), io=14.0GiB (15.0GB), run=60001-60001msec
read_throughput: (g=0): rw=read, bs=(R) 1024KiB-1024KiB, (W) 1024KiB-1024KiB, (T) 1024KiB-1024KiB, ioengine=libaio, iodepth=64

SEQUENTIAL READ: bw=3241MiB/s (3399MB/s), 3241MiB/s-3241MiB/s (3399MB/s-3399MB/s), io=190GiB (204GB), run=60084-60084msec
read_iops: (g=0): rw=randread, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=64

RANDOM READ: bw=979MiB/s (1026MB/s), 979MiB/s-979MiB/s (1026MB/s-1026MB/s), io=57.3GiB (61.6GB), run=60001-60001msec
```

#### Test with proper settings

The setup
```
# make-bcache -C /dev/nvme1n1 -B /dev/mapper/vg1-array --block 4k --bucket 2M --writeback
# mkfs.btrfs -L array /dev/bcache0
# echo 0 > /sys/fs/bcache/bcbec9f6-6278-4475-9865-f7932c749477/congested_write_threshold_us 
# echo 0 > /sys/fs/bcache/bcbec9f6-6278-4475-9865-f7932c749477/congested_read_threshold_us 
# echo 0 > /sys/block/bcache0/bcache/sequential_cutoff 
# echo 8192 > /sys/block/bcache0/queue/read_ahead_kb 
# echo 0 > /sys/class/block/bcache0/bcache/sequential_cutoff
# echo 10 > /sys/class/block/bcache0/bcache/writeback_delay
```

Monitor
```
# cat /sys/class/block/bcache0/bcache/writeback_rate_debug
```

```
root@UNO:~# ./disk-speedtest.sh /mnt/btrfs/
write_throughput: (g=0): rw=write, bs=(R) 1024KiB-1024KiB, (W) 1024KiB-1024KiB, (T) 1024KiB-1024KiB, ioengine=libaio, iodepth=64
...
fio-3.33
Starting 4 processes
write_throughput: Laying out IO file (1 file / 100MiB)
write_throughput: Laying out IO file (1 file / 100MiB)
write_throughput: Laying out IO file (1 file / 100MiB)
write_throughput: Laying out IO file (1 file / 100MiB)
Jobs: 4 (f=4): [W(4)][100.0%][w=931MiB/s][w=931 IOPS][eta 00m:00s] 
write_throughput: (groupid=0, jobs=4): err= 0: pid=23050: Fri Jul 26 21:42:19 2024
  write: IOPS=895, BW=900MiB/s (943MB/s)(52.7GiB/60029msec); 0 zone resets
    slat (usec): min=92, max=780720, avg=4434.61, stdev=24296.21
    clat (usec): min=839, max=1799.0k, avg=280474.09, stdev=181283.72
     lat (msec): min=2, max=1799, avg=284.89, stdev=182.37
    clat percentiles (msec):
     |  1.00th=[   10],  5.00th=[   78], 10.00th=[   87], 20.00th=[  140],
     | 30.00th=[  184], 40.00th=[  220], 50.00th=[  251], 60.00th=[  288],
     | 70.00th=[  330], 80.00th=[  393], 90.00th=[  464], 95.00th=[  567],
     | 99.00th=[ 1020], 99.50th=[ 1133], 99.90th=[ 1536], 99.95th=[ 1653],
     | 99.99th=[ 1754]
   bw (  KiB/s): min=75776, max=3602432, per=99.63%, avg=917983.25, stdev=132677.54, samples=480
   iops        : min=   74, max= 3518, avg=895.97, stdev=129.53, samples=480
  lat (usec)   : 1000=0.01%
  lat (msec)   : 2=0.01%, 4=0.04%, 10=1.01%, 20=1.32%, 50=0.07%
  lat (msec)   : 100=10.10%, 250=36.80%, 500=43.14%, 750=5.63%, 1000=1.18%
  lat (msec)   : 2000=1.15%
  cpu          : usr=1.64%, sys=5.82%, ctx=18874, majf=0, minf=149
  IO depths    : 1=0.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued rwts: total=0,53756,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
  WRITE: bw=900MiB/s (943MB/s), 900MiB/s-900MiB/s (943MB/s-943MB/s), io=52.7GiB (56.6GB), run=60029-60029msec
write_iops: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=64
fio-3.33
Starting 1 process
write_iops: Laying out IO file (1 file / 100MiB)
Jobs: 1 (f=1): [w(1)][100.0%][w=239MiB/s][w=61.2k IOPS][eta 00m:00s]
write_iops: (groupid=0, jobs=1): err= 0: pid=24603: Fri Jul 26 21:43:21 2024
  write: IOPS=61.2k, BW=239MiB/s (251MB/s)(14.0GiB/60001msec); 0 zone resets
    slat (usec): min=3, max=1070.3k, avg=12.66, stdev=753.02
    clat (usec): min=5, max=1071.5k, avg=1032.43, stdev=9103.16
     lat (usec): min=15, max=1071.5k, avg=1045.09, stdev=9146.49
    clat percentiles (usec):
     |  1.00th=[   420],  5.00th=[   457], 10.00th=[   482], 20.00th=[   510],
     | 30.00th=[   537], 40.00th=[   562], 50.00th=[   586], 60.00th=[   619],
     | 70.00th=[   668], 80.00th=[   750], 90.00th=[   922], 95.00th=[  1139],
     | 99.00th=[  2245], 99.50th=[  7898], 99.90th=[120062], 99.95th=[170918],
     | 99.99th=[379585]
   bw (  KiB/s): min=52296, max=382776, per=100.00%, avg=249056.08, stdev=72731.01, samples=118
   iops        : min=13074, max=95694, avg=62264.00, stdev=18182.75, samples=118
  lat (usec)   : 10=0.01%, 20=0.01%, 50=0.02%, 100=0.02%, 250=0.05%
  lat (usec)   : 500=15.77%, 750=64.05%, 1000=12.44%
  lat (msec)   : 2=6.52%, 4=0.41%, 10=0.26%, 20=0.13%, 50=0.10%
  lat (msec)   : 100=0.08%, 250=0.12%, 500=0.01%, 750=0.01%, 2000=0.01%
  cpu          : usr=8.12%, sys=45.92%, ctx=1248496, majf=0, minf=37
  IO depths    : 1=0.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued rwts: total=0,3672584,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
  WRITE: bw=239MiB/s (251MB/s), 239MiB/s-239MiB/s (251MB/s-251MB/s), io=14.0GiB (15.0GB), run=60001-60001msec
read_throughput: (g=0): rw=read, bs=(R) 1024KiB-1024KiB, (W) 1024KiB-1024KiB, (T) 1024KiB-1024KiB, ioengine=libaio, iodepth=64
...
fio-3.33
Starting 4 processes
read_throughput: Laying out IO file (1 file / 100MiB)
read_throughput: Laying out IO file (1 file / 100MiB)
read_throughput: Laying out IO file (1 file / 100MiB)
read_throughput: Laying out IO file (1 file / 100MiB)
Jobs: 4 (f=4): [R(4)][100.0%][r=3241MiB/s][r=3241 IOPS][eta 00m:00s]    
read_throughput: (groupid=0, jobs=4): err= 0: pid=25809: Fri Jul 26 21:44:28 2024
  read: IOPS=3236, BW=3241MiB/s (3399MB/s)(190GiB/60084msec)
    slat (usec): min=14, max=88656, avg=257.26, stdev=1713.18
    clat (msec): min=27, max=238, avg=78.78, stdev=32.51
     lat (msec): min=27, max=238, avg=79.03, stdev=32.48
    clat percentiles (msec):
     |  1.00th=[   35],  5.00th=[   38], 10.00th=[   41], 20.00th=[   48],
     | 30.00th=[   57], 40.00th=[   65], 50.00th=[   74], 60.00th=[   84],
     | 70.00th=[   94], 80.00th=[  107], 90.00th=[  126], 95.00th=[  140],
     | 99.00th=[  167], 99.50th=[  180], 99.90th=[  197], 99.95th=[  207],
     | 99.99th=[  220]
   bw (  MiB/s): min= 2406, max= 4096, per=100.00%, avg=3242.53, stdev=80.05, samples=480
   iops        : min= 2406, max= 4096, avg=3242.13, stdev=80.02, samples=480
  lat (msec)   : 50=22.76%, 100=52.48%, 250=24.89%
  cpu          : usr=0.78%, sys=7.32%, ctx=152306, majf=0, minf=149
  IO depths    : 1=0.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued rwts: total=194490,0,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
   READ: bw=3241MiB/s (3399MB/s), 3241MiB/s-3241MiB/s (3399MB/s-3399MB/s), io=190GiB (204GB), run=60084-60084msec
read_iops: (g=0): rw=randread, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=64
fio-3.33
Starting 1 process
read_iops: Laying out IO file (1 file / 100MiB)
Jobs: 1 (f=1): [r(1)][100.0%][r=954MiB/s][r=244k IOPS][eta 00m:00s]
read_iops: (groupid=0, jobs=1): err= 0: pid=26769: Fri Jul 26 21:45:30 2024
  read: IOPS=251k, BW=979MiB/s (1026MB/s)(57.3GiB/60001msec)
    slat (nsec): min=1881, max=636176, avg=3342.68, stdev=1828.90
    clat (usec): min=38, max=2133, avg=251.91, stdev=59.50
     lat (usec): min=43, max=2136, avg=255.25, stdev=59.62
    clat percentiles (usec):
     |  1.00th=[  172],  5.00th=[  192], 10.00th=[  202], 20.00th=[  212],
     | 30.00th=[  221], 40.00th=[  229], 50.00th=[  237], 60.00th=[  249],
     | 70.00th=[  265], 80.00th=[  285], 90.00th=[  322], 95.00th=[  359],
     | 99.00th=[  457], 99.50th=[  506], 99.90th=[  775], 99.95th=[  832],
     | 99.99th=[ 1004]
   bw (  KiB/s): min=948328, max=1026608, per=100.00%, avg=1002257.60, stdev=13577.43, samples=120
   iops        : min=237082, max=256652, avg=250564.39, stdev=3394.34, samples=120
  lat (usec)   : 50=0.01%, 100=0.02%, 250=61.65%, 500=37.79%, 750=0.43%
  lat (usec)   : 1000=0.10%
  lat (msec)   : 2=0.01%, 4=0.01%
  cpu          : usr=15.33%, sys=84.58%, ctx=2560, majf=0, minf=37
  IO depths    : 1=0.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued rwts: total=15030518,0,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
   READ: bw=979MiB/s (1026MB/s), 979MiB/s-979MiB/s (1026MB/s-1026MB/s), io=57.3GiB (61.6GB), run=60001-60001msec
root@UNO:~# 
```

#### Test before disabling `sequential_cutoff`

```
# ./disk-speedtest.sh /mnt/btrfs/
write_throughput: (g=0): rw=write, bs=(R) 1024KiB-1024KiB, (W) 1024KiB-1024KiB, (T) 1024KiB-1024KiB, ioengine=libaio, iodepth=64
...
fio-3.33
Starting 4 processes
write_throughput: Laying out IO file (1 file / 100MiB)
write_throughput: Laying out IO file (1 file / 100MiB)
write_throughput: Laying out IO file (1 file / 100MiB)
write_throughput: Laying out IO file (1 file / 100MiB)
Jobs: 4 (f=4): [W(4)][100.0%][w=333MiB/s][w=332 IOPS][eta 00m:00s] 
write_throughput: (groupid=0, jobs=4): err= 0: pid=2495693: Fri Jul 26 21:03:01 2024
  write: IOPS=322, BW=327MiB/s (342MB/s)(19.2GiB/60225msec); 0 zone resets
    slat (usec): min=160, max=835640, avg=12424.79, stdev=46702.02
    clat (msec): min=95, max=1671, avg=780.88, stdev=194.44
     lat (msec): min=169, max=1751, avg=793.31, stdev=197.79
    clat percentiles (msec):
     |  1.00th=[  430],  5.00th=[  518], 10.00th=[  558], 20.00th=[  625],
     | 30.00th=[  667], 40.00th=[  709], 50.00th=[  760], 60.00th=[  802],
     | 70.00th=[  844], 80.00th=[  944], 90.00th=[ 1053], 95.00th=[ 1133],
     | 99.00th=[ 1334], 99.50th=[ 1435], 99.90th=[ 1552], 99.95th=[ 1603],
     | 99.99th=[ 1670]
   bw (  KiB/s): min=141381, max=587776, per=99.98%, avg=334266.44, stdev=22297.15, samples=476
   iops        : min=  138, max=  574, avg=326.20, stdev=21.76, samples=476
  lat (msec)   : 100=0.01%, 250=0.16%, 500=3.56%, 750=45.34%, 1000=38.55%
  lat (msec)   : 2000=13.67%
  cpu          : usr=0.42%, sys=13.78%, ctx=27769, majf=0, minf=145
  IO depths    : 1=0.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued rwts: total=0,19408,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
  WRITE: bw=327MiB/s (342MB/s), 327MiB/s-327MiB/s (342MB/s-342MB/s), io=19.2GiB (20.6GB), run=60225-60225msec
write_iops: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=64
fio-3.33
Starting 1 process
write_iops: Laying out IO file (1 file / 100MiB)
Jobs: 1 (f=1): [w(1)][100.0%][w=34.3MiB/s][w=8787 IOPS][eta 00m:00s]
write_iops: (groupid=0, jobs=1): err= 0: pid=2503202: Fri Jul 26 21:04:03 2024
  write: IOPS=4825, BW=18.9MiB/s (19.8MB/s)(1131MiB/60002msec); 0 zone resets
    slat (usec): min=4, max=1267, avg=38.46, stdev=40.69
    clat (usec): min=198, max=316849, avg=13227.27, stdev=22503.92
     lat (usec): min=222, max=316976, avg=13265.74, stdev=22510.48
    clat percentiles (usec):
     |  1.00th=[  1156],  5.00th=[  1975], 10.00th=[  2376], 20.00th=[  2933],
     | 30.00th=[  3458], 40.00th=[  4146], 50.00th=[  5342], 60.00th=[  7504],
     | 70.00th=[ 10290], 80.00th=[ 14746], 90.00th=[ 28705], 95.00th=[ 60031],
     | 99.00th=[121111], 99.50th=[141558], 99.90th=[181404], 99.95th=[196084],
     | 99.99th=[254804]
   bw (  KiB/s): min= 2212, max=41232, per=100.00%, avg=19312.41, stdev=15020.02, samples=120
   iops        : min=  553, max=10308, avg=4827.99, stdev=3755.02, samples=120
  lat (usec)   : 250=0.01%, 500=0.07%, 750=0.22%, 1000=0.34%
  lat (msec)   : 2=4.69%, 4=33.02%, 10=30.71%, 20=17.50%, 50=7.29%
  lat (msec)   : 100=4.29%, 250=1.89%, 500=0.01%
  cpu          : usr=1.89%, sys=17.26%, ctx=60796, majf=0, minf=37
  IO depths    : 1=0.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued rwts: total=0,289545,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
  WRITE: bw=18.9MiB/s (19.8MB/s), 18.9MiB/s-18.9MiB/s (19.8MB/s-19.8MB/s), io=1131MiB (1186MB), run=60002-60002msec
read_throughput: (g=0): rw=read, bs=(R) 1024KiB-1024KiB, (W) 1024KiB-1024KiB, (T) 1024KiB-1024KiB, ioengine=libaio, iodepth=64
...
fio-3.33
Starting 4 processes
read_throughput: Laying out IO file (1 file / 100MiB)
read_throughput: Laying out IO file (1 file / 100MiB)
read_throughput: Laying out IO file (1 file / 100MiB)
read_throughput: Laying out IO file (1 file / 100MiB)
Jobs: 4 (f=4): [R(4)][100.0%][r=700MiB/s][r=699 IOPS][eta 00m:00s]
read_throughput: (groupid=0, jobs=4): err= 0: pid=2511002: Fri Jul 26 21:05:09 2024
  read: IOPS=693, BW=698MiB/s (731MB/s)(41.1GiB/60267msec)
    slat (usec): min=16, max=1576.4k, avg=4304.85, stdev=23143.15
    clat (usec): min=907, max=2073.3k, avg=363868.23, stdev=219438.46
     lat (usec): min=948, max=2073.6k, avg=368169.77, stdev=220339.29
    clat percentiles (msec):
     |  1.00th=[   43],  5.00th=[  104], 10.00th=[  140], 20.00th=[  197],
     | 30.00th=[  243], 40.00th=[  284], 50.00th=[  326], 60.00th=[  368],
     | 70.00th=[  426], 80.00th=[  498], 90.00th=[  617], 95.00th=[  768],
     | 99.00th=[ 1150], 99.50th=[ 1385], 99.90th=[ 1787], 99.95th=[ 2039],
     | 99.99th=[ 2072]
   bw (  KiB/s): min=59440, max=1508788, per=100.00%, avg=730902.84, stdev=65113.80, samples=469
   iops        : min=   58, max= 1472, avg=713.23, stdev=63.54, samples=469
  lat (usec)   : 1000=0.01%
  lat (msec)   : 2=0.06%, 4=0.04%, 10=0.04%, 20=0.15%, 50=1.01%
  lat (msec)   : 100=3.46%, 250=27.50%, 500=48.73%, 750=14.13%, 1000=3.83%
  lat (msec)   : 2000=1.61%, >=2000=0.05%
  cpu          : usr=0.14%, sys=3.80%, ctx=9092, majf=0, minf=146
  IO depths    : 1=0.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued rwts: total=41784,0,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
   READ: bw=698MiB/s (731MB/s), 698MiB/s-698MiB/s (731MB/s-731MB/s), io=41.1GiB (44.1GB), run=60267-60267msec
read_iops: (g=0): rw=randread, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=64
fio-3.33
Starting 1 process
read_iops: Laying out IO file (1 file / 100MiB)
Jobs: 1 (f=1): [r(1)][100.0%][r=983MiB/s][r=252k IOPS][eta 00m:00s]
read_iops: (groupid=0, jobs=1): err= 0: pid=2518279: Fri Jul 26 21:06:12 2024
  read: IOPS=190k, BW=744MiB/s (780MB/s)(43.6GiB/60001msec)
    slat (nsec): min=1808, max=7184.8k, avg=4411.02, stdev=7258.43
    clat (usec): min=67, max=9294, avg=331.25, stdev=375.25
     lat (usec): min=71, max=9324, avg=335.66, stdev=380.09
    clat percentiles (usec):
     |  1.00th=[  192],  5.00th=[  202], 10.00th=[  208], 20.00th=[  219],
     | 30.00th=[  225], 40.00th=[  231], 50.00th=[  237], 60.00th=[  245],
     | 70.00th=[  255], 80.00th=[  269], 90.00th=[  302], 95.00th=[ 1631],
     | 99.00th=[ 2024], 99.50th=[ 2089], 99.90th=[ 2245], 99.95th=[ 2278],
     | 99.99th=[ 2311]
   bw (  KiB/s): min=123896, max=1090160, per=100.00%, avg=762038.44, stdev=353568.08, samples=120
   iops        : min=30974, max=272540, avg=190509.58, stdev=88392.03, samples=120
  lat (usec)   : 100=0.01%, 250=65.15%, 500=29.25%, 750=0.09%, 1000=0.01%
  lat (msec)   : 2=4.23%, 4=1.26%, 10=0.01%
  cpu          : usr=14.86%, sys=85.12%, ctx=650, majf=0, minf=37
  IO depths    : 1=0.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued rwts: total=11428350,0,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
   READ: bw=744MiB/s (780MB/s), 744MiB/s-744MiB/s (780MB/s-780MB/s), io=43.6GiB (46.8GB), run=60001-60001msec
```