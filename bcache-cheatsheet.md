# Bcache

CLI commands, cheatsheet, tricks and learnings from bcache experiment.

### Resources
- https://wiki.archlinux.org/title/User:Sigmike/bcache
- https://sebastian.marsching.com/wiki/bin/view/Linux/Bcache/

### bcache stats

```bash
# cat /sys/fs/bcache/2b65d2e6-c5c6-418f-88df-b0ae1eb6e37f/cache0/priority_stats
Unused:		0%
Clean:		79%
Dirty:		20%
Metadata:	0%
Average:	525
Sectors per Q:	61008512
Quantiles:	[28 60 92 124 156 188 220 252 284 316 348 380 412 451 503 539 571 603 635 667 699 731 763 795 827 859 891 923 955 987 1019]
```

### How much dirty cache, speed of eviction to backing disks?

```bash
# cat /sys/class/block/bcache0/bcache/writeback_rate_debug
rate:		1.2G/sec
dirty:		141.7G
target:		93.1G
proportional:	1.2G
integral:	13.4M
change:		-38.6M/sec
next io:	-2133ms
```

### is cache dirty?

```bash
cat /sys/block/bcache0/bcache/state
```
### CSET for bcache configuration and uuid

```bash
# bcache-super-show /dev/nvme1n1
sb.magic		ok
sb.first_sector		8 [match]
sb.csum			CD7B477E4DF39689 [match]
sb.version		3 [cache device]

dev.label		(empty)
dev.uuid		4716956f-dcb9-46c6-9258-8ba9319f5ff6
dev.sectors_per_block	8
dev.sectors_per_bucket	4096
dev.cache.first_sector	4096
dev.cache.cache_sectors	1953517568
dev.cache.total_sectors	1953521664
dev.cache.ordered	yes
dev.cache.discard	no
dev.cache.pos		0
dev.cache.replacement	0 [lru]

cset.uuid		2b65d2e6-c5c6-418f-88df-b0ae1eb6e37f
```

### Remove all disks from bcache to be able to wipefs

```bash
echo 1 > /sys/fs/bcache/8f63b718-7c97-47d8-8e44-084b2814deaa/unregister
# echo 1 > /sys/block/md127/bcache/stop
# wipefs -a /dev/md127
/dev/md127: 16 bytes were erased at offset 0x00001018 (bcache): c6 85 73 f6 4e 1a 45 ca 82 65 f5 7f 48 ba 6d 81
```

```bash

```

## Setup and speed tweaks to always use cache first

```bash
# make-bcache -C /dev/nvme1n1 -B /dev/mapper/vg1-array --block 4k --bucket 2M --writeback
# mkfs.btrfs -L array /dev/bcache0
# echo 0 > /sys/fs/bcache/bcbec9f6-6278-4475-9865-f7932c749477/congested_write_threshold_us 
# echo 0 > /sys/fs/bcache/bcbec9f6-6278-4475-9865-f7932c749477/congested_read_threshold_us 
# echo 0 > /sys/block/bcache0/bcache/sequential_cutoff 
# echo 8192 > /sys/block/bcache0/queue/read_ahead_kb 
# echo 0 > /sys/class/block/bcache0/bcache/sequential_cutoff
# echo 10 > /sys/class/block/bcache0/bcache/writeback_delay
```

## Remove a cache disk (leave backing storage)

```bash
echo 2b65d2e6-c5c6-418f-88df-b0ae1eb6e37f > /sys/block/bcache0/bcache/detach
echo 1 > /sys/fs/bcache/2b65d2e6-c5c6-418f-88df-b0ae1eb6e37f/stop
```

Verify safe to wipe cache disk (no data)
```bash
# cat /sys/block/bcache0/bcache/state
no cache
# wipefs -a {cache_drive}
```