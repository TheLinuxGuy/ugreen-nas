# Bcache

CLI commands, cheatsheet, tricks and learnings from bcache experiment.

### Resources
- https://wiki.archlinux.org/title/User:Sigmike/bcache
- https://sebastian.marsching.com/wiki/bin/view/Linux/Bcache/
- https://blog.csdn.net/kobe24fgy/article/details/117924858 

## Setup and speed tweaks to always use cache first

Configure optimized settings by TheLinuxGuy
```bash
find /sys/ -type f -name "congested_write_threshold_us" -path "*/bcache/*"  -exec bash -c 'echo 0 > {}' \;
find /sys/ -type f -name "congested_read_threshold_us" -path "*/bcache/*"  -exec bash -c 'echo 0 > {}' \;
find /sys/ -type f -name "writeback_delay" -path "*/bcache/*" -exec bash -c 'echo 10 > {}' \;
find /sys/ -type f -name "writeback_rate_minimum" -path "*/bcache/*" -exec bash -c 'echo 4096 > {}' \;
find /sys/ -type f -name "writeback_percent" -path "*/bcache/*" -exec bash -c 'echo 1 > {}' \;
find /sys/ -type f -name "read_ahead_kb" -path "*/bcache*/queue/*" -exec bash -c 'echo 8192 > {}' \;
```

Check and output all current settings.
```bash
find /sys/ -type f -name "congested_write_threshold_us" -path "*/bcache/*"  -exec bash -c 'echo {}; cat {}' \;
find /sys/ -type f -name "congested_read_threshold_us" -path "*/bcache/*"  -exec bash -c 'echo {}; cat {}'  \;
find /sys/ -type f -name "writeback_delay" -path "*/bcache/*" -exec bash -c 'echo {}; cat {}' \;
find /sys/ -type f -name "writeback_rate_minimum" -path "*/bcache/*" -exec bash -c 'echo {}; cat {}'  \;
find /sys/ -type f -name "writeback_percent" -path "*/bcache/*" -exec bash -c 'echo {}; cat {}'  \;
find /sys/ -type f -name "read_ahead_kb" -path "*/bcache*/queue/*" -exec bash -c 'echo {}; cat {}'  \;
```

Disable cache on backing disks.
```bash
find /sys/ -type f -name "cache_mode" -path "*/bcache/*" -exec bash -c 'echo {}; cat {}'  \;
find /sys/ -type f -name "cache_mode" -path "*/bcache/*" -exec bash -c 'echo none > {}'  \;
```

Set back to writeback
```bash
find /sys/ -type f -name "cache_mode" -path "*/bcache/*" -exec bash -c 'echo writeback > {}'  \;
```

#### NVME/SSD TRIM on bcache aka discard

There are warnings this is dangorous in the Arch Linux wiki. 

A workaround is recommended, to leave 10-20% of disk in separate partition:
- https://lore.kernel.org/linux-bcache/CAC2ZOYvoVfpNh-4hcYxPJkgA9kkK2Scbqg_ce2LO+Xk7D-6drQ@mail.gmail.com/T/ 

```
If you want to make use of trimmed space without using online discard,
your best chance is to create a blank partition on the caching device
after the bcache partition, blkdiscard that, and never touch it. Now
re-create bcache in the first partition. The blank partition should be
around 10-20% of your device size. This way, the SSD firmware can
still do background wear-leveling by swapping flash pages with the
untouched partition and do background gc/erase. This will keep bcache
latency low, and performance should be stable.
```

### Using ZFS on top of bcache requires changes to udev rules

For proxmox, modify
`/usr/lib/udev/rules.d/69-bcache.rules` file with my repo copy.

### bcache stats

```bash
root@UNO:/sys/block/bcache0/bcache/stats_five_minute# grep -H . *
bypassed:0.0k
cache_bypass_hits:0
cache_bypass_misses:0
cache_hit_ratio:87
cache_hits:244
cache_miss_collisions:0
cache_misses:35
```

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

## Remove a cache disk (leave backing storage)

```bash
echo 2b65d2e6-c5c6-418f-88df-b0ae1eb6e37f > /sys/block/bcache0/bcache/detach
echo 1 > /sys/block/md127/bcache/stop
echo 1 > /sys/fs/bcache/2b65d2e6-c5c6-418f-88df-b0ae1eb6e37f/stop
```

Verify safe to wipe cache disk (no data)
```bash
# cat /sys/block/bcache0/bcache/state
no cache
# wipefs -a {cache_drive}
```