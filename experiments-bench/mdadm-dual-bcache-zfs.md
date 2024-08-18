# bcache0 + bcache1

Independent backing setup.
1 nvme cache mdraid.

### Setup

```bash
# echo 0 > /sys/block/bcache0/bcache/sequential_cutoff 
# echo 0 > /sys/block/bcache1/bcache/sequential_cutoff 
# echo 8192 > /sys/block/bcache0/queue/read_ahead_kb 
# echo 8192 > /sys/block/bcache1/queue/read_ahead_kb 
# echo 0 > /sys/class/block/bcache0/bcache/sequential_cutoff
# echo 10 > /sys/class/block/bcache0/bcache/writeback_delay
# echo 0 > /sys/fs/bcache/bc04c7de-9f03-44ac-a41f-296577a27611/congested_write_threshold_us 
# echo 0 > /sys/fs/bcache/bc04c7de-9f03-44ac-a41f-296577a27611/congested_read_threshold_us 
```