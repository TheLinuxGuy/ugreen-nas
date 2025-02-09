# LVM writeback caching (with UGOS settings) 'mq'

### Setup notes LVM2

Resources
- https://christitus.com/lvm-guide/
- https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/5/html/logical_volume_manager_administration/lv
- https://sysadmincasts.com/episodes/27-lvm-linear-vs-striped-logical-volumes 

LVM2 setup
```bash
# pvcreate /dev/md126 /dev/md127
  Physical volume "/dev/md126" successfully created.
  Physical volume "/dev/md127" successfully created.
# vgcreate vg1 /dev/md126 /dev/md127
  Volume group "vg1" successfully created
# lvcreate -n slowsky -l 100%FREE vg1
# pvcreate /dev/md3
root@UNO:~# vgextend vg1 /dev/md3
  Volume group "vg1" successfully extended
root@UNO:~# lvcreate --cache -l 90%FREE -c 2M vg1/slowsky /dev/md3
  Logical volume vg1/slowsky is now cached.
root@UNO:~# lvs -o+kernel_cache_settings vg1/slowsky
  LV      VG  Attr       LSize   Pool          Origin          Data%  Meta%  Move Log Cpy%Sync Convert KCacheSettings
  slowsky vg1 Cwi-a-C--- <23.65t [lvol1_cpool] [slowsky_corig] 0.01   14.19           0.00             migration_threshold=32768
# lvchange --cachepolicy mq --cachesettings 'migration_threshold=8192 random_threshold=0 sequential_threshold=0 discard_promote_adjustment=0 read_promote_adjustment=0 write_promote_adjustment=0' vg1/slowsky
  Logical volume vg1/slowsky changed.
# mkfs.btrfs -L array -f /dev/vg1/slowsky
# mount /dev/vg1/slowsky /mnt/btrfs/
```

change cache to writeback
```bash
root@UNO:~# lvchange --cachemode writeback vg1/slowsky
  Logical volume vg1/slowsky changed.
# lvs -o+cache_mode
  LV      VG  Attr       LSize   Pool          Origin          Data%  Meta%  Move Log Cpy%Sync Convert CacheMode
  slowsky vg1 Cwi-aoC--- <23.65t [lvol1_cpool] [slowsky_corig] 1.76   21.16           4.94             writeback
```
- https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9/html/configuring_and_managing_logical_volumes/enabling-caching-to-improve-logical-volume-performance_configuring-and-managing-logical-volumes#enabling-dm-writecache-caching-for-a-logical-volume_enabling-caching-to-improve-logical-volume-performance

Remove cache, try dm-writecache
```bash
root@UNO:~# lvconvert --uncache vg1/slowsky
root@UNO:~# umount /mnt/btrfs
root@UNO:~# lvchange --activate n vg1/slowsky
root@UNO:~# lvcreate --activate n --size 800G --name writecache vg1 /dev/md3
  WARNING: Logical volume vg1/writecache not zeroed.
  Logical volume "writecache" created.
root@UNO:~# lvconvert --type writecache --cachevol writecache vg1/slowsky
Erase all existing data on vg1/writecache? [y/n]: y
  Logical volume vg1/slowsky now has writecache.
root@UNO:~#
root@UNO:~# lvchange --activate y vg1/slowsky
root@UNO:~# mount /dev/vg1/slowsky /mnt/btrfs/
```

### Tests

#### 'dm-cache' btrfs (while mdadm is rebuilding)

```bash
SEQUENTIAL WRITE: bw=154MiB/s (161MB/s), 154MiB/s-154MiB/s (161MB/s-161MB/s), io=10.6GiB (11.4GB), run=70834-70834msec

RANDOM WRITE: bw=8311KiB/s (8511kB/s), 8311KiB/s-8311KiB/s (8511kB/s-8511kB/s), io=489MiB (513MB), run=60237-60237msec

SEQUENTIAL READ: bw=6496MiB/s (6811MB/s), 6496MiB/s-6496MiB/s (6811MB/s-6811MB/s), io=381GiB (409GB), run=60056-60056msec

RANDOM READ: bw=776MiB/s (814MB/s), 776MiB/s-776MiB/s (814MB/s-814MB/s), io=45.5GiB (48.8GB), run=60001-60001msec
```

#### 'dm-writecache' btrfs (while mdadm is rebuilding)

Writes are improved, but is that it? NVME can write faster than this and it is a raid1 nvme.

```bash
SEQUENTIAL WRITE: bw=603MiB/s (632MB/s), 603MiB/s-603MiB/s (632MB/s-632MB/s), io=35.4GiB (38.1GB), run=60202-60202msec

RANDOM WRITE: bw=244MiB/s (255MB/s), 244MiB/s-244MiB/s (255MB/s-255MB/s), io=14.3GiB (15.3GB), run=60004-60004msec

SEQUENTIAL READ: bw=5626MiB/s (5899MB/s), 5626MiB/s-5626MiB/s (5899MB/s-5899MB/s), io=330GiB (354GB), run=60003-60003msec

RANDOM READ: bw=778MiB/s (816MB/s), 778MiB/s-778MiB/s (816MB/s-816MB/s), io=45.6GiB (48.9GB), run=60001-60001msec
```