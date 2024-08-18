# Filesystem / blockdevice / caching experiments

This folder contains scratch notes on my experiments with multiple virtual block caching technologies and the results I observed. 

A few things I learned a long the way:
- `bcache` is the faster and most performant block cache I tested.
- `Open-CAS` is newer, but limited to ext4 and older filesystems I don't care for.
- `Open-CAS` eats a ridiculous amount of memory. 1TB cache ate 11gb of ram and performance wasn't impressive. 
- Using `LVM2` on top of everything barely has any impacts on performance observed. 
- mdadm-lvm2-bcache-zfs.md saw the most performance across the board on `disk-speedtest.sh` tests. !! AS LONG AS YOU CUSTOMIZE CERTAIN ZFS DEFAULTS !! LVM2 layer seems to improve writes.

Resources:
- https://doc.beegfs.io/latest/advanced_topics/storage_tuning.html 


## Quick commands

`bwm-ng -i disk -I md0,md1,md3`



#### Miscelaneous

NVMEs may not support TRIM. Check

```bash
cat /sys/block/<device>/queue/discard_zeroes_data
0 => TRIM (UNMAP) disabled
1 => TRIM (UNMAP) enabled
```

Verify with nvme-cli tool
- https://nvmexpress.org/wp-content/uploads/NVM-Express-NVM-Command-Set-Specification-1.0c-2022.10.03-Ratified.pdf

```bash
root@UNO:~# nvme id-ns /dev/nvme0n1 -H | grep -A 4 "dlfeat"
dlfeat  : 9
  [4:4] : 0	Guard Field of Deallocated Logical Blocks is set to 0xFFFF
  [3:3] : 0x1	Deallocate Bit in the Write Zeroes Command is Supported
  [2:0] : 0x1	Bytes Read From a Deallocated Logical Block and its Metadata are 0x00
# cat /sys/block/nvme0n1/queue/discard_zeroes_data
0
root@UNO:~# nvme id-ns /dev/nvme1n1 -H | grep -A 4 "dlfeat"
dlfeat  : 0
  [4:4] : 0	Guard Field of Deallocated Logical Blocks is set to 0xFFFF
  [3:3] : 0	Deallocate Bit in the Write Zeroes Command is Not Supported
  [2:0] : 0	Bytes Read From a Deallocated Logical Block and its Metadata are Not Reported

root@UNO:~# nvme id-ns /dev/nvme2n1 -H | grep -A 4 "dlfeat"
dlfeat  : 8
  [4:4] : 0	Guard Field of Deallocated Logical Blocks is set to 0xFFFF
  [3:3] : 0x1	Deallocate Bit in the Write Zeroes Command is Supported
  [2:0] : 0	Bytes Read From a Deallocated Logical Block and its Metadata are Not Reported
  ```