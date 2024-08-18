# lvm2 volume writeback + bcache

### Setup

`/dev/bcache0` is configured as:
- bcache cache (RAID1): /dev/md3
- Backing /dev/mapper/vg1/slowsky
- btrfs

lvmcache layer
- 2TB SSD writeback cache.

lvmcache on 2TB SSD
```bash
root@UNO:~# pvcreate /dev/sda
  Physical volume "/dev/sda" successfully created.
root@UNO:~# vgextend vg1 /dev/sda
  Volume group "vg1" successfully extended
root@UNO:~# vcreate --cache -l 95%FREE -c 2M vg1/slowsky /dev/sda
-bash: vcreate: command not found
root@UNO:~# lvcreate --cache -l 95%FREE -c 2M vg1/slowsky /dev/sda
  Logical volume vg1/slowsky is now cached.
lvchange --cachepolicy mq --cachesettings 'migration_threshold=8192 random_threshold=0 sequential_threshold=0 discard_promote_adjustment=0 read_promote_adjustment=0 write_promote_adjustment=0' vg1/slowsky
```


```bash
root@UNO:~# echo 0 > /sys/fs/bcache/3583a096-8787-4aa6-9443-1a8173457885/congested_write_threshold_us
root@UNO:~# echo 0 > /sys/fs/bcache/3583a096-8787-4aa6-9443-1a8173457885/congested_read_threshold_us
root@UNO:~# echo 0 > /sys/block/bcache0/bcache/sequential_cutoff
root@UNO:~# echo 16384 > /sys/block/bcache0/queue/read_ahead_kb
root@UNO:~# echo 0 > /sys/class/block/bcache0/bcache/sequential_cutoff
root@UNO:~# echo 10 > /sys/class/block/bcache0/bcache/writeback_delay
```

### Bench (mdadm still rebuilding the raid5 backing storage)

#### btrfs (ssd cache on lvm, nvme on bcache)

```bash
SEQUENTIAL WRITE: IOPS=1042, BW=1047MiB/s (1098MB/s)(61.4GiB/60041msec); 0 zone resets

RANDOM WRITE: IOPS=51.0k, BW=199MiB/s (209MB/s)(11.7GiB/60006msec); 0 zone resets

SEQUENTIAL READ: IOPS=6255, BW=6260MiB/s (6564MB/s)(367GiB/60056msec)

RANDOM READ: IOPS=210k, BW=819MiB/s (859MB/s)(48.0GiB/60001msec)
```

#### ext4 (ssd cache on lvm, nvme on bcache)

```bash
SEQUENTIAL WRITE: IOPS=961, BW=965MiB/s (1012MB/s)(56.6GiB/60025msec); 0 zone resets

RANDOM WRITE: IOPS=40.3k, BW=157MiB/s (165MB/s)(9435MiB/60002msec); 0 zone resets

SEQUENTIAL READ: IOPS=6167, BW=6172MiB/s (6471MB/s)(362GiB/60054msec)

RANDOM READ: IOPS=282k, BW=1100MiB/s (1153MB/s)(64.4GiB/60001msec)
```

#### zfs (ssd cache on lvm, nvme on bcache)

```bash
echo 4096 > /sys/devices/virtual/block/dm-3/bcache/writeback_rate_minimum

SEQUENTIAL WRITE: IOPS=961, BW=965MiB/s (1012MB/s)(56.6GiB/60025msec); 0 zone resets

RANDOM WRITE: IOPS=40.3k, BW=157MiB/s (165MB/s)(9435MiB/60002msec); 0 zone resets

SEQUENTIAL READ: IOPS=6167, BW=6172MiB/s (6471MB/s)(362GiB/60054msec)

RANDOM READ: IOPS=282k, BW=1100MiB/s (1153MB/s)(64.4GiB/60001msec)

```