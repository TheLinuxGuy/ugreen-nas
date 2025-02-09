# mdadm + bcache + zfs
Let's remove LVM2 from the mix. Does performance increase?

### Setup

```bash

# make-bcache -C /dev/nvme1n1 -B /dev/md127 --block 4k --bucket 2M --writeback --wipe-bcache
zpool create -f -o ashift=13 -O atime=off -O compression=lz4 bcache /dev/bcache0
# mount /dev/bcache0 /mnt/btrfs/
# echo 0 > /sys/fs/bcache/db0f97bf-5a9a-479d-850a-8ee97c355d01/congested_write_threshold_us 
# echo 0 > /sys/fs/bcache/db0f97bf-5a9a-479d-850a-8ee97c355d01/congested_read_threshold_us 
# echo 0 > /sys/block/bcache0/bcache/sequential_cutoff 
# echo 8192 > /sys/block/bcache0/queue/read_ahead_kb 
# echo 0 > /sys/class/block/bcache0/bcache/sequential_cutoff 
# echo 10 > /sys/class/block/bcache0/bcache/writeback_delay 
```

### ZFS tweakorooo

```bash
# echo 0 > /sys/module/zfs/parameters/zfs_prefetch_disable 
# echo 10 > /sys/module/zfs/parameters/zfs_txg_timeout 
# echo 2147483648 > /sys/module/zfs/parameters/l2arc_write_max 
# echo 2147483648 > /sys/module/zfs/parameters/l2arc_write_boost 
# echo 0 > /sys/module/zfs/parameters/l2arc_headroom
# echo 0 > /sys/module/zfs/parameters/l2arc_noprefetch   
# echo 1 > /sys/module/zfs/parameters/l2arc_rebuild_enabled 
```

### Results

```bash
SEQUENTIAL WRITE: bw=264MiB/s (277MB/s), 264MiB/s-264MiB/s (277MB/s-277MB/s), io=17.0GiB (18.2GB), run=66000-66000msec

RANDOM WRITE: bw=739MiB/s (775MB/s), 739MiB/s-739MiB/s (775MB/s-775MB/s), io=43.3GiB (46.5GB), run=60001-60001msec

SEQUENTIAL READ: bw=9.81GiB/s (10.5GB/s), 9.81GiB/s-9.81GiB/s (10.5GB/s-10.5GB/s), io=589GiB (632GB), run=60001-60001msec

RANDOM READ: bw=329MiB/s (345MB/s), 329MiB/s-329MiB/s (345MB/s-345MB/s), io=19.3GiB (20.7GB), run=60001-60001msec
```

#### Before tweaking zfs settings

```bash
SEQUENTIAL WRITE: bw=381MiB/s (400MB/s), 381MiB/s-381MiB/s (400MB/s-400MB/s), io=22.6GiB (24.2GB), run=60693-60693msec

RANDOM WRITE: bw=757MiB/s (794MB/s), 757MiB/s-757MiB/s (794MB/s-794MB/s), io=44.3GiB (47.6GB), run=60001-60001msec

SEQUENTIAL READ: bw=9866MiB/s (10.3GB/s), 9866MiB/s-9866MiB/s (10.3GB/s-10.3GB/s), io=578GiB (621GB), run=60001-60001msec

RANDOM READ: bw=331MiB/s (347MB/s), 331MiB/s-331MiB/s (347MB/s-347MB/s), io=19.4GiB (20.8GB), run=60001-60001msec
```