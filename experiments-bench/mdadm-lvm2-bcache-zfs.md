# mdadm + lvm2 + bcache + zfs

What is this:
- Add bcache to the mix
- RAID5 mdadm on all physical disks (8TB + 8TB + 10TB + 10TB)
- Use partitions, mimic Synology flexible RAID to use different sized disks
- LVM2 to tie this together via LVs
- zfs filesystem

### Setup notes


```bash
# make-bcache -C /dev/nvme1n1 -B /dev/mapper/vg1-slowsky --block 4k --bucket 2M --writeback
# echo 0 > /sys/fs/bcache/db0f97bf-5a9a-479d-850a-8ee97c355d01/congested_write_threshold_us 
# echo 0 > /sys/fs/bcache/db0f97bf-5a9a-479d-850a-8ee97c355d01/congested_read_threshold_us 
# echo 0 > /sys/block/bcache0/bcache/sequential_cutoff 
# echo 16348 > /sys/block/bcache0/queue/read_ahead_kb 
# echo 0 > /sys/class/block/bcache0/bcache/sequential_cutoff 
# echo 10 > /sys/class/block/bcache0/bcache/writeback_delay 
echo 4096 > /sys/devices/virtual/block/dm-0/bcache/writeback_rate_minimum
echo 10 > /sys/devices/virtual/block/dm-0/bcache/writeback_delay
# zpool create -o ashift=13 -O atime=off -O compression=lz4 pool /dev/bcache0
```

```bash
echo 1 > /sys/block/dm-0/bcache/stop
echo /dev/mapper/vg1-slowsky > /sys/fs/bcache/register
```

performance check.
`cat /sys/devices/virtual/block/dm-0/bcache/writeback_rate_debug`

Best results are with extra weeks at the bottom.

TL;DR on the best results.
```
SEQUENTIAL WRITE: bw=1176MiB/s (1233MB/s), 1176MiB/s-1176MiB/s (1233MB/s-1233MB/s), io=69.3GiB (74.4GB), run=60320-60320msec

RANDOM WRITE: bw=1298MiB/s (1361MB/s), 1298MiB/s-1298MiB/s (1361MB/s-1361MB/s), io=76.1GiB (81.7GB), run=60001-60001msec

SEQUENTIAL READ: bw=10.4GiB/s (11.1GB/s), 10.4GiB/s-10.4GiB/s (11.1GB/s-11.1GB/s), io=622GiB (667GB), run=60001-60001msec

RANDOM READ: bw=496MiB/s (520MB/s), 496MiB/s-496MiB/s (520MB/s-520MB/s), io=29.1GiB (31.2GB), run=60001-60001msec
```

### ZFS specific settings

```
# cat /sys/module/zfs/parameters/zfs_prefetch_disable
0
# cat /sys/module/zfs/parameters/zfs_txg_timeout
10
# cat /sys/module/zfs/parameters/l2arc_write_max
2147483648
# cat /sys/module/zfs/parameters/l2arc_write_boost
2147483648
# cat /sys/module/zfs/parameters/l2arc_headroom
0
# cat /sys/module/zfs/parameters/l2arc_noprefetch
0
# cat /sys/module/zfs/parameters/l2arc_rebuild_enabled
1
```

### Test results summary (without extra tweaks)

The best results was the proper settings below.

TL;DR
```bash
SEQUENTIAL WRITE: bw=1057MiB/s (1108MB/s), 1057MiB/s-1057MiB/s (1108MB/s-1108MB/s), io=62.0GiB (66.5GB), run=60017-60017msec

RANDOM WRITE: bw=1295MiB/s (1358MB/s), 1295MiB/s-1295MiB/s (1358MB/s-1358MB/s), io=75.9GiB (81.5GB), run=60001-60001msec

SEQUENTIAL READ: bw=9868MiB/s (10.3GB/s), 9868MiB/s-9868MiB/s (10.3GB/s-10.3GB/s), io=578GiB (621GB), run=60002-60002msec

RANDOM READ: bw=359MiB/s (376MB/s), 359MiB/s-359MiB/s (376MB/s-376MB/s), io=21.0GiB (22.6GB), run=60001-60001mse
```

### Test 2 - extra tweaks - improved random read

```
# echo 0 > /sys/module/zfs/parameters/zfs_prefetch_disable 
# echo 10 > /sys/module/zfs/parameters/zfs_txg_timeout 
# echo 2147483648 > /sys/module/zfs/parameters/l2arc_write_max 
# echo 2147483648 > /sys/module/zfs/parameters/l2arc_write_boost 
# echo 0 > /sys/module/zfs/parameters/l2arc_headroom
# echo 0 > /sys/module/zfs/parameters/l2arc_noprefetch 
# echo 1 > /sys/module/zfs/parameters/l2arc_rebuild_enabled 
```

TL;DR
```
SEQUENTIAL WRITE: bw=1176MiB/s (1233MB/s), 1176MiB/s-1176MiB/s (1233MB/s-1233MB/s), io=69.3GiB (74.4GB), run=60320-60320msec

RANDOM WRITE: bw=1298MiB/s (1361MB/s), 1298MiB/s-1298MiB/s (1361MB/s-1361MB/s), io=76.1GiB (81.7GB), run=60001-60001msec

SEQUENTIAL READ: bw=10.4GiB/s (11.1GB/s), 10.4GiB/s-10.4GiB/s (11.1GB/s-11.1GB/s), io=622GiB (667GB), run=60001-60001msec

RANDOM READ: bw=496MiB/s (520MB/s), 496MiB/s-496MiB/s (520MB/s-520MB/s), io=29.1GiB (31.2GB), run=60001-60001msec
```

sysbench
```
root@UNO:/pool# sysbench fileio --file-test-mode=rndrd --file-total-size=10G --file-block-size=4K --threads=4 --time=60 run
sysbench 1.0.20 (using bundled LuaJIT 2.1.0-beta2)

Running the test with following options:
Number of threads: 4
Initializing random number generator from current time


Extra file open flags: (none)
128 files, 80MiB each
10GiB total file size
Block size 4KiB
Number of IO requests: 0
Read/Write ratio for combined random IO test: 1.50
Periodic FSYNC enabled, calling fsync() each 100 requests.
Calling fsync() at the end of test, Enabled.
Using synchronous I/O mode
Doing random read test
Initializing worker threads...

Threads started!


File operations:
    reads/s:                      406841.30
    writes/s:                     0.00
    fsyncs/s:                     0.00

Throughput:
    read, MiB/s:                  1589.22
    written, MiB/s:               0.00

General statistics:
    total time:                          60.0001s
    total number of events:              24410995

Latency (ms):
         min:                                    0.00
         avg:                                    0.01
         max:                                    3.63
         95th percentile:                        0.01
         sum:                               234807.03

Threads fairness:
    events (avg/stddev):           6102748.7500/909526.23
    execution time (avg/stddev):   58.7018/0.02

root@UNO:/pool# 

```


## ZFS arc

TLDR 786MB arc size max.

```
# arc_summary 

------------------------------------------------------------------------
ZFS Subsystem Report                            Fri Jul 26 22:19:36 2024
Linux 6.8.8-2-pve                                             2.2.4-pve1
Machine: UNO (x86_64)                                         2.2.4-pve1

ARC status:                                                      HEALTHY
        Memory throttle count:                                         0

ARC size (current):                                    14.2 %  106.5 MiB
        Target size (adaptive):                       100.0 %  750.0 MiB
        Min size (hard limit):                         50.0 %  375.0 MiB
        Max size (high water):                            2:1  750.0 MiB
        Anonymous data size:                            0.1 %  136.0 KiB
        Anonymous metadata size:                        0.0 %    0 Bytes
        MFU data target:                               78.9 %   72.7 MiB
        MFU data size:                                 18.2 %   16.8 MiB
        MFU ghost data size:                                     0 Bytes
        MFU metadata target:                            9.1 %    8.4 MiB
        MFU metadata size:                             15.6 %   14.3 MiB
        MFU ghost metadata size:                                 0 Bytes
        MRU data target:                                2.8 %    2.6 MiB
        MRU data size:                                 40.9 %   37.6 MiB
        MRU ghost data size:                                     0 Bytes
        MRU metadata target:                            9.1 %    8.4 MiB
        MRU metadata size:                             25.2 %   23.2 MiB
        MRU ghost metadata size:                                 0 Bytes
        Uncached data size:                             0.0 %    0 Bytes
        Uncached metadata size:                         0.0 %    0 Bytes
        Bonus size:                                     2.1 %    2.2 MiB
        Dnode cache target:                            10.0 %   75.0 MiB
        Dnode cache size:                              10.2 %    7.7 MiB
        Dbuf size:                                      3.1 %    3.3 MiB
        Header size:                                    0.8 %  878.9 KiB
        L2 header size:                                 0.0 %    0 Bytes
        ABD chunk waste size:                           0.4 %  407.5 KiB

ARC hash breakdown:
        Elements max:                                               9.5k
        Elements current:                              37.1 %       3.5k
        Collisions:                                                  439
        Chain max:                                                     1
        Chains:                                                        1

ARC misc:
        Deleted:                                                   97.2k
        Mutex misses:                                                 58
        Eviction skips:                                            76.5k
        Eviction skips due to L2 writes:                               0
        L2 cached evictions:                                     0 Bytes
        L2 eligible evictions:                                  18.4 GiB
        L2 eligible MFU evictions:                      3.2 %  610.4 MiB
        L2 eligible MRU evictions:                     96.8 %   17.8 GiB
        L2 ineligible evictions:                                22.7 MiB

ARC total accesses:                                                18.8M
        Total hits:                                    99.9 %      18.8M
        Total I/O hits:                               < 0.1 %       3.0k
        Total misses:                                   0.1 %      12.4k

ARC demand data accesses:                              52.9 %      10.0M
        Demand data hits:                             100.0 %      10.0M
        Demand data I/O hits:                         < 0.1 %        114
        Demand data misses:                           < 0.1 %       4.1k

ARC demand metadata accesses:                          47.0 %       8.8M
        Demand metadata hits:                         100.0 %       8.8M
        Demand metadata I/O hits:                     < 0.1 %        124
        Demand metadata misses:                       < 0.1 %       1.6k

ARC prefetch data accesses:                             0.1 %      11.9k
        Prefetch data hits:                            50.6 %       6.0k
        Prefetch data I/O hits:                         0.0 %          0
        Prefetch data misses:                          49.4 %       5.9k

ARC prefetch metadata accesses:                       < 0.1 %       8.8k
        Prefetch metadata hits:                        59.5 %       5.2k
        Prefetch metadata I/O hits:                    31.4 %       2.8k
        Prefetch metadata misses:                       9.1 %        794

ARC predictive prefetches:                             99.9 %      20.6k
        Demand hits after predictive:                  60.9 %      12.6k
        Demand I/O hits after predictive:               0.9 %        182
        Never demanded after predictive:               38.2 %       7.9k

ARC prescient prefetches:                               0.1 %         22
        Demand hits after prescient:                   72.7 %         16
        Demand I/O hits after prescient:               27.3 %          6
        Never demanded after prescient:                 0.0 %          0

ARC states hits of all accesses:
        Most frequently used (MFU):                    97.4 %      18.3M
        Most recently used (MRU):                       2.6 %     481.7k
        Most frequently used (MFU) ghost:             < 0.1 %       3.4k
        Most recently used (MRU) ghost:               < 0.1 %        405
        Uncached:                                       0.0 %          0

DMU predictive prefetcher calls:                                   22.3M
        Stream hits:                                    3.7 %     822.5k
        Stream misses:                                 96.3 %      21.5M
        Streams limit reached:                         99.5 %      21.4M
        Prefetches issued                                          10.4k

L2ARC not detected, skipping section

Solaris Porting Layer (SPL):
        spl_hostid                                                     0
        spl_hostid_path                                      /etc/hostid
        spl_kmem_alloc_max                                       1048576
        spl_kmem_alloc_warn                                        65536
        spl_kmem_cache_kmem_threads                                    4
        spl_kmem_cache_magazine_size                                   0
        spl_kmem_cache_max_size                                       32
        spl_kmem_cache_obj_per_slab                                    8
        spl_kmem_cache_slab_limit                                  16384
        spl_max_show_tasks                                           512
        spl_panic_halt                                                 0
        spl_schedule_hrtimeout_slack_us                                0
        spl_taskq_kick                                                 0
        spl_taskq_thread_bind                                          0
        spl_taskq_thread_dynamic                                       1
        spl_taskq_thread_priority                                      1
        spl_taskq_thread_sequential                                    4
        spl_taskq_thread_timeout_ms                                 5000

Tunables:
        brt_zap_default_bs                                            12
        brt_zap_default_ibs                                           12
        brt_zap_prefetch                                               1
        dbuf_cache_hiwater_pct                                        10
        dbuf_cache_lowater_pct                                        10
        dbuf_cache_max_bytes                        18446744073709551615
        dbuf_cache_shift                                               5
        dbuf_metadata_cache_max_bytes               18446744073709551615
        dbuf_metadata_cache_shift                                      6
        dbuf_mutex_cache_shift                                         0
        ddt_zap_default_bs                                            15
        ddt_zap_default_ibs                                           15
        dmu_object_alloc_chunk_shift                                   7
        dmu_prefetch_max                                       134217728
        icp_aes_impl                cycle [fastest] generic x86_64 aesni
        icp_gcm_avx_chunk_size                                     32736
        icp_gcm_impl               cycle [fastest] avx generic pclmulqdq
        ignore_hole_birth                                              1
        l2arc_exclude_special                                          0
        l2arc_feed_again                                               1
        l2arc_feed_min_ms                                            200
        l2arc_feed_secs                                                1
        l2arc_headroom                                                 2
        l2arc_headroom_boost                                         200
        l2arc_meta_percent                                            33
        l2arc_mfuonly                                                  0
        l2arc_noprefetch                                               1
        l2arc_norw                                                     0
        l2arc_rebuild_blocks_min_l2size                       1073741824
        l2arc_rebuild_enabled                                          1
        l2arc_trim_ahead                                               0
        l2arc_write_boost                                        8388608
        l2arc_write_max                                          8388608
        metaslab_aliquot                                         1048576
        metaslab_bias_enabled                                          1
        metaslab_debug_load                                            0
        metaslab_debug_unload                                          0
        metaslab_df_max_search                                  16777216
        metaslab_df_use_largest_segment                                0
        metaslab_force_ganging                                  16777217
        metaslab_force_ganging_pct                                     3
        metaslab_fragmentation_factor_enabled                          1
        metaslab_lba_weighting_enabled                                 1
        metaslab_preload_enabled                                       1
        metaslab_preload_limit                                        10
        metaslab_preload_pct                                          50
        metaslab_unload_delay                                         32
        metaslab_unload_delay_ms                                  600000
        send_holes_without_birth_time                                  1
        spa_asize_inflation                                           24
        spa_config_path                             /etc/zfs/zpool.cache
        spa_load_print_vdev_tree                                       0
        spa_load_verify_data                                           1
        spa_load_verify_metadata                                       1
        spa_load_verify_shift                                          4
        spa_slop_shift                                                 5
        spa_upgrade_errlog_limit                                       0
        vdev_file_logical_ashift                                       9
        vdev_file_physical_ashift                                      9
        vdev_removal_max_span                                      32768
        vdev_validate_skip                                             0
        zap_iterate_prefetch                                           1
        zap_micro_max_size                                        131072
        zfetch_hole_shift                                              2
        zfetch_max_distance                                     67108864
        zfetch_max_idistance                                    67108864
        zfetch_max_reorder                                      16777216
        zfetch_max_sec_reap                                            2
        zfetch_max_streams                                             8
        zfetch_min_distance                                      4194304
        zfetch_min_sec_reap                                            1
        zfs_abd_scatter_enabled                                        1
        zfs_abd_scatter_max_order                                      9
        zfs_abd_scatter_min_size                                    1536
        zfs_admin_snapshot                                             0
        zfs_allow_redacted_dataset_mount                               0
        zfs_arc_average_blocksize                                   8192
        zfs_arc_dnode_limit                                            0
        zfs_arc_dnode_limit_percent                                   10
        zfs_arc_dnode_reduce_percent                                  10
        zfs_arc_evict_batch_limit                                     10
        zfs_arc_eviction_pct                                         200
        zfs_arc_grow_retry                                             0
        zfs_arc_lotsfree_percent                                      10
        zfs_arc_max                                            786432000
        zfs_arc_meta_balance                                         500
        zfs_arc_min                                                    0
        zfs_arc_min_prefetch_ms                                        0
        zfs_arc_min_prescient_prefetch_ms                              0
        zfs_arc_pc_percent                                             0
        zfs_arc_prune_task_threads                                     1
        zfs_arc_shrink_shift                                           0
        zfs_arc_shrinker_limit                                     10000
        zfs_arc_sys_free                                               0
        zfs_async_block_max_blocks                  18446744073709551615
        zfs_autoimport_disable                                         1
        zfs_bclone_enabled                                             0
        zfs_bclone_wait_dirty                                          0
        zfs_blake3_impl          cycle [fastest] generic sse2 sse41 avx2
        zfs_btree_verify_intensity                                     0
        zfs_checksum_events_per_second                                20
        zfs_commit_timeout_pct                                        10
        zfs_compressed_arc_enabled                                     1
        zfs_condense_indirect_commit_entry_delay_ms                    0
        zfs_condense_indirect_obsolete_pct                            25
        zfs_condense_indirect_vdevs_enable                             1
        zfs_condense_max_obsolete_bytes                       1073741824
        zfs_condense_min_mapping_bytes                            131072
        zfs_dbgmsg_enable                                              1
        zfs_dbgmsg_maxsize                                       4194304
        zfs_dbuf_state_index                                           0
        zfs_ddt_data_is_special                                        1
        zfs_deadman_checktime_ms                                   60000
        zfs_deadman_enabled                                            1
        zfs_deadman_failmode                                        wait
        zfs_deadman_synctime_ms                                   600000
        zfs_deadman_ziotime_ms                                    300000
        zfs_dedup_prefetch                                             0
        zfs_default_bs                                                 9
        zfs_default_ibs                                               17
        zfs_delay_min_dirty_percent                                   60
        zfs_delay_scale                                           500000
        zfs_delete_blocks                                          20480
        zfs_dirty_data_max                                    4177978982
        zfs_dirty_data_max_max                                4294967296
        zfs_dirty_data_max_max_percent                                25
        zfs_dirty_data_max_percent                                    10
        zfs_dirty_data_sync_percent                                   20
        zfs_disable_ivset_guid_check                                   0
        zfs_dmu_offset_next_sync                                       1
        zfs_embedded_slog_min_ms                                      64
        zfs_expire_snapshot                                          300
        zfs_fallocate_reserve_percent                                110
        zfs_flags                                                      0
        zfs_fletcher_4_impl [fastest] scalar superscalar superscalar4 sse2 ssse3 avx2
        zfs_free_bpobj_enabled                                         1
        zfs_free_leak_on_eio                                           0
        zfs_free_min_time_ms                                        1000
        zfs_history_output_max                                   1048576
        zfs_immediate_write_sz                                     32768
        zfs_initialize_chunk_size                                1048576
        zfs_initialize_value                        16045690984833335022
        zfs_keep_log_spacemaps_at_export                               0
        zfs_key_max_salt_uses                                  400000000
        zfs_livelist_condense_new_alloc                                0
        zfs_livelist_condense_sync_cancel                              0
        zfs_livelist_condense_sync_pause                               0
        zfs_livelist_condense_zthr_cancel                              0
        zfs_livelist_condense_zthr_pause                               0
        zfs_livelist_max_entries                                  500000
        zfs_livelist_min_percent_shared                               75
        zfs_lua_max_instrlimit                                 100000000
        zfs_lua_max_memlimit                                   104857600
        zfs_max_async_dedup_frees                                 100000
        zfs_max_dataset_nesting                                       50
        zfs_max_log_walking                                            5
        zfs_max_logsm_summary_length                                  10
        zfs_max_missing_tvds                                           0
        zfs_max_nvlist_src_size                                        0
        zfs_max_recordsize                                      16777216
        zfs_metaslab_find_max_tries                                  100
        zfs_metaslab_fragmentation_threshold                          70
        zfs_metaslab_max_size_cache_sec                             3600
        zfs_metaslab_mem_limit                                        25
        zfs_metaslab_segment_weight_enabled                            1
        zfs_metaslab_switch_threshold                                  2
        zfs_metaslab_try_hard_before_gang                              0
        zfs_mg_fragmentation_threshold                                95
        zfs_mg_noalloc_threshold                                       0
        zfs_min_metaslabs_to_flush                                     1
        zfs_multihost_fail_intervals                                  10
        zfs_multihost_history                                          0
        zfs_multihost_import_intervals                                20
        zfs_multihost_interval                                      1000
        zfs_multilist_num_sublists                                     0
        zfs_no_scrub_io                                                0
        zfs_no_scrub_prefetch                                          0
        zfs_nocacheflush                                               0
        zfs_nopwrite_enabled                                           1
        zfs_object_mutex_size                                         64
        zfs_obsolete_min_time_ms                                     500
        zfs_override_estimate_recordsize                               0
        zfs_pd_bytes_max                                        52428800
        zfs_per_txg_dirty_frees_percent                               30
        zfs_prefetch_disable                                           0
        zfs_read_history                                               0
        zfs_read_history_hits                                          0
        zfs_rebuild_max_segment                                  1048576
        zfs_rebuild_scrub_enabled                                      1
        zfs_rebuild_vdev_limit                                  67108864
        zfs_reconstruct_indirect_combinations_max                   4096
        zfs_recover                                                    0
        zfs_recv_best_effort_corrective                                0
        zfs_recv_queue_ff                                             20
        zfs_recv_queue_length                                   16777216
        zfs_recv_write_batch_size                                1048576
        zfs_removal_ignore_errors                                      0
        zfs_removal_suspend_progress                                   0
        zfs_remove_max_segment                                  16777216
        zfs_resilver_disable_defer                                     0
        zfs_resilver_min_time_ms                                    3000
        zfs_scan_blkstats                                              0
        zfs_scan_checkpoint_intval                                  7200
        zfs_scan_fill_weight                                           3
        zfs_scan_ignore_errors                                         0
        zfs_scan_issue_strategy                                        0
        zfs_scan_legacy                                                0
        zfs_scan_max_ext_gap                                     2097152
        zfs_scan_mem_lim_fact                                         20
        zfs_scan_mem_lim_soft_fact                                    20
        zfs_scan_report_txgs                                           0
        zfs_scan_strict_mem_lim                                        0
        zfs_scan_suspend_progress                                      0
        zfs_scan_vdev_limit                                     16777216
        zfs_scrub_error_blocks_per_txg                              4096
        zfs_scrub_min_time_ms                                       1000
        zfs_send_corrupt_data                                          0
        zfs_send_no_prefetch_queue_ff                                 20
        zfs_send_no_prefetch_queue_length                        1048576
        zfs_send_queue_ff                                             20
        zfs_send_queue_length                                   16777216
        zfs_send_unmodified_spill_blocks                               1
        zfs_sha256_impl cycle [fastest] generic x64 ssse3 avx avx2 shani
        zfs_sha512_impl             cycle [fastest] generic x64 avx avx2
        zfs_slow_io_events_per_second                                 20
        zfs_snapshot_history_enabled                                   1
        zfs_spa_discard_memory_limit                            16777216
        zfs_special_class_metadata_reserve_pct                        25
        zfs_sync_pass_deferred_free                                    2
        zfs_sync_pass_dont_compress                                    8
        zfs_sync_pass_rewrite                                          2
        zfs_sync_taskq_batch_pct                                      75
        zfs_traverse_indirect_prefetch_limit                          32
        zfs_trim_extent_bytes_max                              134217728
        zfs_trim_extent_bytes_min                                  32768
        zfs_trim_metaslab_skip                                         0
        zfs_trim_queue_limit                                          10
        zfs_trim_txg_batch                                            32
        zfs_txg_history                                              100
        zfs_txg_timeout                                                5
        zfs_unflushed_log_block_max                               131072
        zfs_unflushed_log_block_min                                 1000
        zfs_unflushed_log_block_pct                                  400
        zfs_unflushed_log_txg_max                                   1000
        zfs_unflushed_max_mem_amt                             1073741824
        zfs_unflushed_max_mem_ppm                                   1000
        zfs_unlink_suspend_progress                                    0
        zfs_user_indirect_is_special                                   1
        zfs_vdev_aggregation_limit                               1048576
        zfs_vdev_aggregation_limit_non_rotating                   131072
        zfs_vdev_async_read_max_active                                 3
        zfs_vdev_async_read_min_active                                 1
        zfs_vdev_async_write_active_max_dirty_percent                 60
        zfs_vdev_async_write_active_min_dirty_percent                 30
        zfs_vdev_async_write_max_active                               10
        zfs_vdev_async_write_min_active                                2
        zfs_vdev_def_queue_depth                                      32
        zfs_vdev_default_ms_count                                    200
        zfs_vdev_default_ms_shift                                     29
        zfs_vdev_disk_classic                                          1
        zfs_vdev_disk_max_segs                                         0
        zfs_vdev_failfast_mask                                         1
        zfs_vdev_initializing_max_active                               1
        zfs_vdev_initializing_min_active                               1
        zfs_vdev_max_active                                         1000
        zfs_vdev_max_auto_ashift                                      14
        zfs_vdev_max_ms_shift                                         34
        zfs_vdev_min_auto_ashift                                       9
        zfs_vdev_min_ms_count                                         16
        zfs_vdev_mirror_non_rotating_inc                               0
        zfs_vdev_mirror_non_rotating_seek_inc                          1
        zfs_vdev_mirror_rotating_inc                                   0
        zfs_vdev_mirror_rotating_seek_inc                              5
        zfs_vdev_mirror_rotating_seek_offset                     1048576
        zfs_vdev_ms_count_limit                                   131072
        zfs_vdev_nia_credit                                            5
        zfs_vdev_nia_delay                                             5
        zfs_vdev_open_timeout_ms                                    1000
        zfs_vdev_queue_depth_pct                                    1000
        zfs_vdev_raidz_impl cycle [fastest] original scalar sse2 ssse3 avx2
        zfs_vdev_read_gap_limit                                    32768
        zfs_vdev_rebuild_max_active                                    3
        zfs_vdev_rebuild_min_active                                    1
        zfs_vdev_removal_max_active                                    2
        zfs_vdev_removal_min_active                                    1
        zfs_vdev_scheduler                                        unused
        zfs_vdev_scrub_max_active                                      3
        zfs_vdev_scrub_min_active                                      1
        zfs_vdev_sync_read_max_active                                 10
        zfs_vdev_sync_read_min_active                                 10
        zfs_vdev_sync_write_max_active                                10
        zfs_vdev_sync_write_min_active                                10
        zfs_vdev_trim_max_active                                       2
        zfs_vdev_trim_min_active                                       1
        zfs_vdev_write_gap_limit                                    4096
        zfs_vnops_read_chunk_size                                1048576
        zfs_wrlog_data_max                                    8355957964
        zfs_xattr_compat                                               0
        zfs_zevent_len_max                                           512
        zfs_zevent_retain_expire_secs                                900
        zfs_zevent_retain_max                                       2000
        zfs_zil_clean_taskq_maxalloc                             1048576
        zfs_zil_clean_taskq_minalloc                                1024
        zfs_zil_clean_taskq_nthr_pct                                 100
        zfs_zil_saxattr                                                1
        zil_maxblocksize                                          131072
        zil_maxcopied                                               7680
        zil_nocacheflush                                               0
        zil_replay_disable                                             0
        zil_slog_bulk                                           67108864
        zio_deadman_log_all                                            0
        zio_dva_throttle_enabled                                       1
        zio_requeue_io_start_cut_in_line                               1
        zio_slow_io_ms                                             30000
        zio_taskq_batch_pct                                           80
        zio_taskq_batch_tpq                                            0
        zio_taskq_read                         fixed,1,8 null scale null
        zio_taskq_write                  batch fixed,1,5 scale fixed,1,5
        zstd_abort_size                                           131072
        zstd_earlyabort_pass                                           1
        zvol_blk_mq_blocks_per_thread                                  8
        zvol_blk_mq_queue_depth                                      128
        zvol_enforce_quotas                                            1
        zvol_inhibit_dev                                               0
        zvol_major                                                   230
        zvol_max_discard_blocks                                    16384
        zvol_num_taskqs                                                0
        zvol_open_timeout_ms                                        1000
        zvol_prefetch_bytes                                       131072
        zvol_request_sync                                              0
        zvol_threads                                                   0
        zvol_use_blk_mq                                                0
        zvol_volmode                                                   1

ZIL committed transactions:                                        30.6k
        Commit requests:                                             147
        Flushes to stable storage:                                   147
        Transactions to SLOG storage pool:            0 Bytes          0
        Transactions to non-SLOG storage pool:      114.2 MiB       1.0k

# 

```