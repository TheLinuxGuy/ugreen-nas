# Filesystem / blockdevice / caching experiments

This folder contains scratch notes on my experiments with multiple virtual block caching technologies and the results I observed. 

A few things I learned a long the way:
- `bcache` is the faster and most performant block cache I tested.
- `Open-CAS` is newer, but limited to ext4 and older filesystems I don't care for.
- `Open-CAS` eats a ridiculous amount of memory. 1TB cache ate 11gb of ram and performance wasn't impressive. 
- Using `LVM2` on top of everything barely has any impacts on performance observed. 
- mdadm-lvm2-bcache-zfs.md saw the most performance across the board on `disk-speedtest.sh` tests. !! AS LONG AS YOU CUSTOMIZE CERTAIN ZFS DEFAULTS !! LVM2 layer seems to improve writes.


## Quick commands

`bwm-ng -i disk -I md0,md1,md3`

