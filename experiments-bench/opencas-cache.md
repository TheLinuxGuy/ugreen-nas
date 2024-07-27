# OpenCAS cache

Resources: 
- https://github.com/josehu07/open-cas-linux-mf?tab=readme-ov-file#usage 
- https://open-cas.com/getting_started_open_cas_linux.html 

```bash
root@UNO:~/open-cas-linux# casadm -V
╔═════════════════════════╤═════════════════════╗
║ Name                    │       Version       ║
╠═════════════════════════╪═════════════════════╣
║ CAS Cache Kernel Module │ 22.12.0.0855.master ║
║ CAS CLI Utility         │ 22.12.0.0855.master ║
╚═════════════════════════╧═════════════════════╝
```

## TheLinuxGuy TL;DR test results
### Ext4 on /dev/cas1-1
```bash
# mkfs.ext4 /dev/cas1-1
# TLDR
SEQUENTIAL WRITE: bw=906MiB/s (950MB/s), 906MiB/s-906MiB/s (950MB/s-950MB/s), io=53.1GiB (57.0GB), run=60032-60032msec

RANDOM WRITE: bw=610MiB/s (640MB/s), 610MiB/s-610MiB/s (640MB/s-640MB/s), io=35.8GiB (38.4GB), run=60025-60025msec

SEQUENTIAL READ: bw=1426MiB/s (1495MB/s), 1426MiB/s-1426MiB/s (1495MB/s-1495MB/s), io=83.6GiB (89.7GB), run=60014-60014msec

RANDOM READ: bw=1070MiB/s (1122MB/s), 1070MiB/s-1070MiB/s (1122MB/s-1122MB/s), io=62.7GiB (67.3GB), run=60001-60001msec
```

### Btrfs on /dev/cas1-1
```bash
mkfs.btrfs -L array -f /dev/cas1-1
# TLDR
SEQUENTIAL WRITE: bw=753MiB/s (790MB/s), 753MiB/s-753MiB/s (790MB/s-790MB/s), io=44.2GiB (47.4GB), run=60032-60032msec

RANDOM WRITE: bw=272MiB/s (285MB/s), 272MiB/s-272MiB/s (285MB/s-285MB/s), io=15.9GiB (17.1GB), run=60005-60005msec

SEQUENTIAL READ: bw=1404MiB/s (1472MB/s), 1404MiB/s-1404MiB/s (1472MB/s-1472MB/s), io=82.3GiB (88.4GB), run=60019-60019msec

RANDOM READ: bw=805MiB/s (844MB/s), 805MiB/s-805MiB/s (844MB/s-844MB/s), io=47.2GiB (50.7GB), run=60001-60001msec
```

## Commands cheatsheet

https://open-cas.com/guide_tool_details.html 

### Check & clear stats

Clear stats
```bash
casadm -Z -i 1
```

Stats example
```bash
# casadm -P -i 1
Cache Id                  1
Cache Size                241643190 [4KiB Blocks] / 921.80 [GiB]
Cache Device              /dev/nvme1n1
Exported Object           -
Core Devices              1
Inactive Core Devices     0
Write Policy              wb
Cleaning Policy           nop
Promotion Policy          always
Cache line size           4 [KiB]
Metadata Memory Footprint 10.6 [GiB]
Dirty for                 0 [s] / Cache clean
Status                    Running

╔══════════════════╤═══════════╤══════╤═════════════╗
║ Usage statistics │   Count   │  %   │   Units     ║
╠══════════════════╪═══════════╪══════╪═════════════╣
║ Occupancy        │   8728641 │  3.6 │ 4KiB Blocks ║
║ Free             │ 232914549 │ 96.4 │ 4KiB Blocks ║
║ Clean            │   8728641 │  3.6 │ 4KiB Blocks ║
║ Dirty            │         0 │  0.0 │ 4KiB Blocks ║
╚══════════════════╧═══════════╧══════╧═════════════╝

╔══════════════════════╤═══════╤═══════╤══════════╗
║ Request statistics   │ Count │   %   │ Units    ║
╠══════════════════════╪═══════╪═══════╪══════════╣
║ Read hits            │ 10827 │  92.2 │ Requests ║
║ Read partial misses  │     0 │   0.0 │ Requests ║
║ Read full misses     │   914 │   7.8 │ Requests ║
║ Read total           │ 11741 │ 100.0 │ Requests ║
╟──────────────────────┼───────┼───────┼──────────╢
║ Write hits           │     0 │   0.0 │ Requests ║
║ Write partial misses │     0 │   0.0 │ Requests ║
║ Write full misses    │     0 │   0.0 │ Requests ║
║ Write total          │     0 │   0.0 │ Requests ║
╟──────────────────────┼───────┼───────┼──────────╢
║ Pass-Through reads   │     0 │   0.0 │ Requests ║
║ Pass-Through writes  │     0 │   0.0 │ Requests ║
║ Serviced requests    │ 11741 │ 100.0 │ Requests ║
╟──────────────────────┼───────┼───────┼──────────╢
║ Total requests       │ 11741 │ 100.0 │ Requests ║
╚══════════════════════╧═══════╧═══════╧══════════╝

╔══════════════════════════════════╤═════════╤═══════╤═════════════╗
║ Block statistics                 │  Count  │   %   │   Units     ║
╠══════════════════════════════════╪═════════╪═══════╪═════════════╣
║ Reads from core(s)               │  523776 │ 100.0 │ 4KiB Blocks ║
║ Writes to core(s)                │       0 │   0.0 │ 4KiB Blocks ║
║ Total to/from core(s)            │  523776 │ 100.0 │ 4KiB Blocks ║
╟──────────────────────────────────┼─────────┼───────┼─────────────╢
║ Reads from cache                 │ 8204736 │  94.0 │ 4KiB Blocks ║
║ Writes to cache                  │  523776 │   6.0 │ 4KiB Blocks ║
║ Total to/from cache              │ 8728512 │ 100.0 │ 4KiB Blocks ║
╟──────────────────────────────────┼─────────┼───────┼─────────────╢
║ Reads from exported object(s)    │ 8728512 │ 100.0 │ 4KiB Blocks ║
║ Writes to exported object(s)     │       0 │   0.0 │ 4KiB Blocks ║
║ Total to/from exported object(s) │ 8728512 │ 100.0 │ 4KiB Blocks ║
╚══════════════════════════════════╧═════════╧═══════╧═════════════╝

╔════════════════════╤═══════╤═════╤══════════╗
║ Error statistics   │ Count │  %  │ Units    ║
╠════════════════════╪═══════╪═════╪══════════╣
║ Cache read errors  │     0 │ 0.0 │ Requests ║
║ Cache write errors │     0 │ 0.0 │ Requests ║
║ Cache total errors │     0 │ 0.0 │ Requests ║
╟────────────────────┼───────┼─────┼──────────╢
║ Core read errors   │     0 │ 0.0 │ Requests ║
║ Core write errors  │     0 │ 0.0 │ Requests ║
║ Core total errors  │     0 │ 0.0 │ Requests ║
╟────────────────────┼───────┼─────┼──────────╢
║ Total errors       │     0 │ 0.0 │ Requests ║
╚════════════════════╧═══════╧═════╧══════════╝
```

### Check if a cache is running.
```bash
# casadm -L
type    id   disk           status    write policy   device
cache   1    /dev/nvme1n1   Running   wb             -
└core   1    /dev/md127     Active    -              /dev/cas1-1
```

### Get stats of cache
```bash
casadm -P -i 1
```

### Get sequential IO cutoff configuration
```bash
casadm -G -n seq-cutoff  -i 1 -j 1
```

### Set sequential IO policy to never to write always to cache
```bash
casadm -X -n seq-cutoff -i 1 -j 1 -p never -t 1024
```

### Promotion policy from backing storage to cache
```bash
# casadm -G -n promotion  -i 1
╔═══════════════════════╤════════╗
║ Parameter name        │ Value  ║
╠═══════════════════════╪════════╣
║ Promotion policy type │ always ║
╚═══════════════════════╧════════╝
```

### cleaning
```bash
# casadm -G -n cleaning -i 1
╔══════════════════════╤═══════╗
║ Parameter name       │ Value ║
╠══════════════════════╪═══════╣
║ Cleaning policy type │ nop   ║
╚══════════════════════╧═══════╝
# set it to nop
 casadm -X -n cleaning -i 1 -p nop
```

### cleaning-acp
```bash
# casadm -G -n cleaning-acp -i 1
╔═══════════════════╤═══════╗
║ Parameter name    │ Value ║
╠═══════════════════╪═══════╣
║ Wake up time [ms] │    10 ║
║ Flush max buffers │   128 ║
╚═══════════════════╧═══════╝
# set it 
casadm -X -n cleaning-acp -i 1 -w XX -b XX
```
### Enable / set writeback mode
```bash
casadm -Q -c wb -i 1 -f yes
```

### ALRU settings
```bash
# casadm -G -n cleaning-alru -i 1
╔═════════════════════════╤═══════╗
║ Parameter name          │ Value ║
╠═════════════════════════╪═══════╣
║ Wake up time [s]        │    20 ║
║ Stale buffer time [s]   │   120 ║
║ Flush max buffers       │   100 ║
║ Activity threshold [ms] │ 10000 ║
╚═════════════════════════╧═══════╝
root@UNO:~/open-cas-linux#
```

### Promotion
```bash
# casadm -G -n promotion -i 1
╔═══════════════════════╤════════╗
║ Parameter name        │ Value  ║
╠═══════════════════════╪════════╣
║ Promotion policy type │ always ║
╚═══════════════════════╧════════╝
```

### Promotion NHIT
```bash
# casadm -G -n promotion-nhit -i 1
╔═════════════════════╤═══════╗
║ Parameter name      │ Value ║
╠═════════════════════╪═══════╣
║ Insertion threshold │     3 ║
║ Policy trigger [%]  │    80 ║
╚═════════════════════╧═══════╝
```

## Setup

```bash
root@UNO:~/open-cas-linux# ls -lah /dev/disk/by-id/nvme-WD_Red_SN700_1000GB_240551802364
lrwxrwxrwx 1 root root 13 Jul 27 16:11 /dev/disk/by-id/nvme-WD_Red_SN700_1000GB_240551802364 -> ../../nvme1n1
root@UNO:~/open-cas-linux# casadm -S -d /dev/disk/by-id/nvme-WD_Red_SN700_1000GB_240551802364
Successfully added cache instance 1
root@UNO:~/open-cas-linux# ls -lah /dev/disk/by-id/md-name-UNO\:large
lrwxrwxrwx 1 root root 11 Jul 27 18:34 /dev/disk/by-id/md-name-UNO:large -> ../../md127
root@UNO:~/open-cas-linux# casadm -A -d /dev/disk/by-id/md-name-UNO:large -i 1
Successfully added core 1 to cache instance 1
root@UNO:~/open-cas-linux# casadm -L

type    id   disk           status    write policy   device
cache   1    /dev/nvme1n1   Running   wt             -
└core   1    /dev/md127     Active    -              /dev/cas1-1
```