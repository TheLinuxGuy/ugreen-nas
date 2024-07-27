# mdadm + lvm2 + btrfs

What is this:
- RAID5 mdadm on all physical disks (8TB + 8TB + 10TB + 10TB)
- Use partitions, mimic Synology flexible RAID to use different sized disks
- LVM2 to tie this together via LVs
- btrfs filesystem

### Test results

TLDR
```
SEQUENTIAL WRITE: bw=311MiB/s (326MB/s), 311MiB/s-311MiB/s (326MB/s-326MB/s), io=18.3GiB (19.6GB), run=60171-60171msec

RANDOM WRITE: bw=19.7MiB/s (20.6MB/s), 19.7MiB/s-19.7MiB/s (20.6MB/s-20.6MB/s), io=1182MiB (1239MB), run=60039-60039msec

SEQUENTIAL READ: bw=645MiB/s (676MB/s), 645MiB/s-645MiB/s (676MB/s-676MB/s), io=38.0GiB (40.8GB), run=60323-60323msec

RANDOM READ: bw=75.5MiB/s (79.2MB/s), 75.5MiB/s-75.5MiB/s (79.2MB/s-79.2MB/s), io=4530MiB
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
Jobs: 4 (f=4): [W(4)][100.0%][w=412MiB/s][w=412 IOPS][eta 00m:00s] 
write_throughput: (groupid=0, jobs=4): err= 0: pid=2381203: Fri Jul 26 20:46:47 2024
  write: IOPS=307, BW=311MiB/s (326MB/s)(18.3GiB/60171msec); 0 zone resets
    slat (usec): min=141, max=498314, avg=13022.41, stdev=50670.66
    clat (msec): min=99, max=1510, avg=818.60, stdev=205.87
     lat (msec): min=170, max=1526, avg=831.64, stdev=209.28
    clat percentiles (msec):
     |  1.00th=[  359],  5.00th=[  527], 10.00th=[  592], 20.00th=[  651],
     | 30.00th=[  693], 40.00th=[  743], 50.00th=[  785], 60.00th=[  852],
     | 70.00th=[  911], 80.00th=[ 1020], 90.00th=[ 1116], 95.00th=[ 1167],
     | 99.00th=[ 1318], 99.50th=[ 1385], 99.90th=[ 1418], 99.95th=[ 1418],
     | 99.99th=[ 1502]
   bw (  KiB/s): min=108544, max=645456, per=98.96%, avg=315404.48, stdev=25303.63, samples=480
   iops        : min=  106, max=  630, avg=307.87, stdev=24.69, samples=480
  lat (msec)   : 100=0.01%, 250=0.49%, 500=3.11%, 750=38.71%, 1000=37.57%
  lat (msec)   : 2000=21.47%
  cpu          : usr=0.37%, sys=12.86%, ctx=5379, majf=0, minf=149
  IO depths    : 1=0.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued rwts: total=0,18473,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
  WRITE: bw=311MiB/s (326MB/s), 311MiB/s-311MiB/s (326MB/s-326MB/s), io=18.3GiB (19.6GB), run=60171-60171msec
write_iops: (g=0): rw=randwrite, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=64
fio-3.33
Starting 1 process
write_iops: Laying out IO file (1 file / 100MiB)
Jobs: 1 (f=1): [w(1)][100.0%][w=26.4MiB/s][w=6750 IOPS][eta 00m:00s]
write_iops: (groupid=0, jobs=1): err= 0: pid=2388672: Fri Jul 26 20:47:50 2024
  write: IOPS=5036, BW=19.7MiB/s (20.6MB/s)(1182MiB/60039msec); 0 zone resets
    slat (usec): min=3, max=1150, avg=31.15, stdev=31.11
    clat (usec): min=136, max=342391, avg=12687.58, stdev=22515.99
     lat (usec): min=152, max=342441, avg=12718.74, stdev=22521.32
    clat percentiles (usec):
     |  1.00th=[   971],  5.00th=[  1663], 10.00th=[  2089], 20.00th=[  2638],
     | 30.00th=[  3130], 40.00th=[  3851], 50.00th=[  5080], 60.00th=[  7046],
     | 70.00th=[  9503], 80.00th=[ 13698], 90.00th=[ 26870], 95.00th=[ 58983],
     | 99.00th=[120062], 99.50th=[137364], 99.90th=[181404], 99.95th=[214959],
     | 99.99th=[250610]
   bw (  KiB/s): min= 2320, max=45416, per=100.00%, avg=20170.97, stdev=15248.19, samples=120
   iops        : min=  580, max=11354, avg=5042.64, stdev=3812.06, samples=120
  lat (usec)   : 250=0.01%, 500=0.12%, 750=0.37%, 1000=0.61%
  lat (msec)   : 2=7.72%, 4=32.88%, 10=30.01%, 20=15.74%, 50=6.33%
  lat (msec)   : 100=4.30%, 250=1.91%, 500=0.01%
  cpu          : usr=1.68%, sys=15.15%, ctx=17814, majf=0, minf=37
  IO depths    : 1=0.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued rwts: total=0,302413,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
  WRITE: bw=19.7MiB/s (20.6MB/s), 19.7MiB/s-19.7MiB/s (20.6MB/s-20.6MB/s), io=1182MiB (1239MB), run=60039-60039msec
read_throughput: (g=0): rw=read, bs=(R) 1024KiB-1024KiB, (W) 1024KiB-1024KiB, (T) 1024KiB-1024KiB, ioengine=libaio, iodepth=64
...
fio-3.33
Starting 4 processes
read_throughput: Laying out IO file (1 file / 100MiB)
read_throughput: Laying out IO file (1 file / 100MiB)
read_throughput: Laying out IO file (1 file / 100MiB)
read_throughput: Laying out IO file (1 file / 100MiB)
Jobs: 2 (f=2): [_(1),R(1),_(1),R(1)][100.0%][r=567MiB/s][r=566 IOPS][eta 00m:00s]
read_throughput: (groupid=0, jobs=4): err= 0: pid=2396245: Fri Jul 26 20:48:55 2024
  read: IOPS=640, BW=645MiB/s (676MB/s)(38.0GiB/60323msec)
    slat (usec): min=14, max=5755.7k, avg=6184.53, stdev=54038.86
    clat (usec): min=1418, max=6209.5k, avg=392081.66, stdev=433190.39
     lat (usec): min=1465, max=6250.5k, avg=398286.27, stdev=438037.97
    clat percentiles (msec):
     |  1.00th=[   21],  5.00th=[   52], 10.00th=[  125], 20.00th=[  186],
     | 30.00th=[  226], 40.00th=[  271], 50.00th=[  317], 60.00th=[  372],
     | 70.00th=[  443], 80.00th=[  531], 90.00th=[  667], 95.00th=[  852],
     | 99.00th=[ 1284], 99.50th=[ 1720], 99.90th=[ 5873], 99.95th=[ 5873],
     | 99.99th=[ 6074]
   bw (  KiB/s): min=81969, max=1987274, per=100.00%, avg=717557.28, stdev=85330.94, samples=441
   iops        : min=   80, max= 1940, avg=700.29, stdev=83.30, samples=441
  lat (msec)   : 2=0.02%, 4=0.10%, 10=0.14%, 20=0.71%, 50=4.04%
  lat (msec)   : 100=3.04%, 250=27.55%, 500=41.39%, 750=16.47%, 1000=4.17%
  lat (msec)   : 2000=2.55%, >=2000=0.49%
  cpu          : usr=0.14%, sys=1.96%, ctx=7679, majf=0, minf=145
  IO depths    : 1=0.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued rwts: total=38654,0,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
   READ: bw=645MiB/s (676MB/s), 645MiB/s-645MiB/s (676MB/s-676MB/s), io=38.0GiB (40.8GB), run=60323-60323msec
read_iops: (g=0): rw=randread, bs=(R) 4096B-4096B, (W) 4096B-4096B, (T) 4096B-4096B, ioengine=libaio, iodepth=64
fio-3.33
Starting 1 process
read_iops: Laying out IO file (1 file / 100MiB)
Jobs: 1 (f=1): [r(1)][100.0%][r=73.7MiB/s][r=18.9k IOPS][eta 00m:00s]
read_iops: (groupid=0, jobs=1): err= 0: pid=2403558: Fri Jul 26 20:49:58 2024
  read: IOPS=19.3k, BW=75.5MiB/s (79.2MB/s)(4530MiB/60012msec)
    slat (nsec): min=1871, max=10890k, avg=17055.99, stdev=19324.24
    clat (usec): min=2, max=94433, avg=3293.66, stdev=5438.62
     lat (usec): min=65, max=94461, avg=3310.72, stdev=5438.19
    clat percentiles (usec):
     |  1.00th=[   79],  5.00th=[   92], 10.00th=[  111], 20.00th=[  149],
     | 30.00th=[  192], 40.00th=[  289], 50.00th=[  482], 60.00th=[  668],
     | 70.00th=[  988], 80.00th=[ 8586], 90.00th=[12518], 95.00th=[14746],
     | 99.00th=[18220], 99.50th=[21890], 99.90th=[33817], 99.95th=[38011],
     | 99.99th=[48497]
   bw (  KiB/s): min=65330, max=84064, per=100.00%, avg=77330.79, stdev=2823.91, samples=120
   iops        : min=16332, max=21016, avg=19332.67, stdev=706.00, samples=120
  lat (usec)   : 4=0.01%, 20=0.01%, 50=0.01%, 100=7.55%, 250=29.94%
  lat (usec)   : 500=13.61%, 750=12.50%, 1000=6.60%
  lat (msec)   : 2=4.42%, 4=0.66%, 10=8.39%, 20=15.67%, 50=0.65%
  lat (msec)   : 100=0.01%
  cpu          : usr=6.50%, sys=37.51%, ctx=443432, majf=0, minf=37
  IO depths    : 1=0.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=100.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.1%, >=64=0.0%
     issued rwts: total=1159622,0,0,0 short=0,0,0,0 dropped=0,0,0,0
     latency   : target=0, window=0, percentile=100.00%, depth=64

Run status group 0 (all jobs):
   READ: bw=75.5MiB/s (79.2MB/s), 75.5MiB/s-75.5MiB/s (79.2MB/s-79.2MB/s), io=4530MiB (4750MB), run=60012-60012msec
root@UNO:~# cat /proc/mdstat 
Personalities : [raid6] [raid5] [raid4] [raid1] 
md126 : active raid1 sdc2[1] sdd2[0]
      1952277440 blocks super 1.2 [2/2] [UU]
      bitmap: 0/15 pages [0KB], 65536KB chunk

md127 : active raid5 sdc1[4] sdd1[2] sdf1[1] sde1[0]
      23441064960 blocks super 1.2 level 5, 512k chunk, algorithm 2 [4/4] [UUUU]
      bitmap: 0/59 pages [0KB], 65536KB chunk

unused devices: <none>

```