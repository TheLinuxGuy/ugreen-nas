# Baseline information (to cache or not)

## mdadm RAID5 (3 disks) raw bcache with backing storage only.

440Mb/s

```
root@UNO:~# pv /dev/bcache0 > /dev/null
12.6GiB 0:00:50 [ 439MiB/s] [>                                                                                               ]  0% ETA 1:00:32:39
14.4GiB 0:00:54 [ 466MiB/s] [>                                                                                                 ]  0% ETA 23:17:33
22.3GiB 0:01:11 [ 449MiB/s] [>                                                                                                 ]  0% ETA 19:45:11
24.8GiB 0:01:16 [ 418MiB/s] [>                                                                                                 ]  0% ETA 19:02:35
^C.2GiB 0:01:17 [ 429MiB/s] [>                                                                                                 ]  0% ETA 18:58:12
root@UNO:~#
```