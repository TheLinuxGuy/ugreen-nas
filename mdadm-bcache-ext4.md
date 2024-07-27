# MDADM ext4 + bcache (no lvm)

What this is:
- RAID5 mdadm on all physical disks (8TB + 8TB + 10TB + 10TB)
- ext4 format
- bcache0 is RAID5 + cache nvme disk.

### Test results

TLDR
```
SEQUENTIAL WRITE: bw=524MiB/s (550MB/s), 524MiB/s-524MiB/s (550MB/s-550MB/s), io=30.9GiB (33.1GB), run=60284-60284msec

RANDOM WRITE: bw=128MiB/s (134MB/s), 128MiB/s-128MiB/s (134MB/s-134MB/s), io=7689MiB (8063MB), run=60009-60009msec

SEQUENTIAL READ: bw=3869MiB/s (4057MB/s), 3869MiB/s-3869MiB/s (4057MB/s-4057MB/s), io=227GiB (244GB), run=60117-60117msec

RANDOM READ: bw=1206MiB/s (1265MB/s), 1206MiB/s-1206MiB/s (1265MB/s-1265MB/s), io=70.7GiB (75.9GB), run=60001-60001msec
```