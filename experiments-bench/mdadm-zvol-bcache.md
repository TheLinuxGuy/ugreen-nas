# mdadm + zfs (for cache) + bcache + btrfs

What is this:
- RAID5 mdadm on all physical disks (8TB + 8TB + 10TB + 10TB)
- nvme cache is zfs


### Setup

`/dev/zvol/bcache/cache` zvol for bcache cache device.
`/dev/md127` slow storage RAID5.

```bash
# zpool create -f -o ashift=13 -O atime=off -O compression=lz4 bcache /dev/nvme1n1
# zfs create -V 850G bcache/cache
# make-bcache -C /dev/zvol/bcache/cache -B /dev/md127 --block 4k --bucket 2M --writeback --wipe-bcache
# mkfs.btrfs -L array -f /dev/bcache0
# mount /dev/bcache0 /mnt/btrfs/
# echo 0 > /sys/fs/bcache/db0f97bf-5a9a-479d-850a-8ee97c355d01/congested_write_threshold_us 
# echo 0 > /sys/fs/bcache/db0f97bf-5a9a-479d-850a-8ee97c355d01/congested_read_threshold_us 
# echo 0 > /sys/block/bcache0/bcache/sequential_cutoff 
# echo 8192 > /sys/block/bcache0/queue/read_ahead_kb 
# echo 0 > /sys/class/block/bcache0/bcache/sequential_cutoff 
# echo 10 > /sys/class/block/bcache0/bcache/writeback_delay 
```

Zvol probably will cause overhead: https://www.reddit.com/r/zfs/comments/16xiio7/using_zvols_for_block_devices/

### Test results (zvol is bcache "cache" device)

TL;DR - horrible write speeds. Don't use zvols as bcache block device. Too much overhead.

```bash
SEQUENTIAL WRITE: bw=153MiB/s (160MB/s), 153MiB/s-153MiB/s (160MB/s-160MB/s), io=12.0GiB (12.9GB), run=80303-80303msec

RANDOM WRITE: bw=18.7MiB/s (19.7MB/s), 18.7MiB/s-18.7MiB/s (19.7MB/s-19.7MB/s), io=1125MiB (1180MB), run=60037-60037msec

SEQUENTIAL READ: bw=6533MiB/s (6850MB/s), 6533MiB/s-6533MiB/s (6850MB/s-6850MB/s), io=383GiB (411GB), run=60012-60012msec

RANDOM READ: bw=992MiB/s (1040MB/s), 992MiB/s-992MiB/s (1040MB/s-1040MB/s), io=58.1GiB (62.4GB), run=60001-60001msec
```