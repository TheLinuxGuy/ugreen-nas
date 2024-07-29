# lvm2 volume writeback + bcache



```bash
root@UNO:~# echo 0 > /sys/fs/bcache/3583a096-8787-4aa6-9443-1a8173457885/congested_write_threshold_us
root@UNO:~# echo 0 > /sys/fs/bcache/3583a096-8787-4aa6-9443-1a8173457885/congested_read_threshold_us
root@UNO:~# echo 0 > /sys/block/bcache0/bcache/sequential_cutoff
root@UNO:~# echo 16384 > /sys/block/bcache0/queue/read_ahead_kb
root@UNO:~# echo 0 > /sys/class/block/bcache0/bcache/sequential_cutoff
root@UNO:~# echo 10 > /sys/class/block/bcache0/bcache/writeback_delay
```