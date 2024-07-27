# MDADM Flex RAID with ZFS

What this is:
- RAID5 mdadm on all physical disks (8TB + 8TB + 10TB + 10TB)
- Use partitions, mimic Synology flexible RAID to use different sized disks
- ZFS formatted into both mdadm raids to combine space into a single zpool (no redundancy on zfs level, we get it at mdadm level)
- No Bcache... we rely only on zfs cache.

### Test results

TLDR
```
SEQUENTIAL WRITE: bw=130MiB/s (137MB/s), 130MiB/s-130MiB/s (137MB/s-137MB/s), io=7991MiB (8379MB), run=61265-61265msec

RANDOM WRITE: bw=1196MiB/s (1254MB/s), 1196MiB/s-1196MiB/s (1254MB/s-1254MB/s), io=70.1GiB (75.3GB), run=60001-60001msec

SEQUENTIAL READ: bw=9.91GiB/s (10.6GB/s), 9.91GiB/s-9.91GiB/s (10.6GB/s-10.6GB/s), io=595GiB (638GB), run=60001-60001msec

RANDOM READ: bw=390MiB/s (409MB/s), 390MiB/s-390MiB/s (409MB/s-409MB/s), io=22.8GiB (24.5GB), run=60001-60001msec
```

## Settings

```
root@UNO:~# cat /sys/module/zfs/parameters/zfs_prefetch_disable
0
root@UNO:~# cat /sys/module/zfs/parameters/zfs_txg_timeout
10
root@UNO:~# cat /sys/module/zfs/parameters/l2arc_write_max
2147483648
root@UNO:~# cat /sys/module/zfs/parameters/l2arc_write_boost
2147483648
root@UNO:~# cat /sys/module/zfs/parameters/l2arc_headroom
0
root@UNO:~# cat /sys/module/zfs/parameters/l2arc_noprefetch
0
root@UNO:~# cat /sys/module/zfs/parameters/l2arc_rebuild_enabled
1
```