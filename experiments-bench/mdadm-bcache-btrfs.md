# mdadm + bcache + btrfs (no LVM)

What is this:
- bcache
- RAID5 mdadm on 3 disks
- Use partitions
- btrfs filesystem directly on mdadm

Compare results. TL;DR No noticeable performance improvement or degradation by skipping LVM in the setup and going direct to mdadm.

We actually lost flexibility raid from the /dev/md127 (1.8TB of wasted space that we gained via LVM2)

## Setup

```
# make-bcache -C /dev/nvme1n1 -B /dev/md126 --block 4k --bucket 2M --writeback --wipe-bcache
# mount /dev/bcache0 /mnt/btrfs/
# mkfs.btrfs -L array /dev/bcache0
# echo 0 > /sys/fs/bcache/bcbec9f6-6278-4475-9865-f7932c749477/congested_write_threshold_us 
# echo 0 > /sys/fs/bcache/bcbec9f6-6278-4475-9865-f7932c749477/congested_read_threshold_us 
# echo 0 > /sys/block/bcache0/bcache/sequential_cutoff 
# echo 8192 > /sys/block/bcache0/queue/read_ahead_kb 
# echo 0 > /sys/class/block/bcache0/bcache/sequential_cutoff
# echo 10 > /sys/class/block/bcache0/bcache/writeback_delay
```

## Test results


TL;DR
```
SEQUENTIAL WRITE: bw=1093MiB/s (1146MB/s), 1093MiB/s-1093MiB/s (1146MB/s-1146MB/s), io=64.1GiB (68.8GB), run=60032-60032msec

RANDOM WRITE: bw=261MiB/s (274MB/s), 261MiB/s-261MiB/s (274MB/s-274MB/s), io=15.3GiB (16.5GB), run=60108-60108msec

SEQUENTIAL READ: bw=3251MiB/s (3409MB/s), 3251MiB/s-3251MiB/s (3409MB/s-3409MB/s), io=191GiB (205GB), run=60073-60073msec

RANDOM READ: bw=975MiB/s (1022MB/s), 975MiB/s-975MiB/s (1022MB/s-1022MB/s), io=57.1GiB (61.3GB), run=60001-60001msec
```