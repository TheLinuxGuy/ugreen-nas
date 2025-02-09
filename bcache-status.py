#!/usr/bin/env python3
# TheLinuxGuy clone of below gist.
# https://gist.github.com/froloffw7/8e1103f1d7dee6fd9a6cc80043fcbf66
#
# Dumb script to dump (some) of bcache status
# Copyright 2013 Darrick J. Wong. All rights reserved.
#
# This file is part of Bcache.  Bcache is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import os
import sys
import argparse
from datetime import timedelta, datetime
from time import sleep

MAX_KEY_LENGTH    = 28
DEV_BLOCK_PATH    = '/dev/block/'
SYSFS_BCACHE_PATH = '/sys/fs/bcache/'
SYSFS_BLOCK_PATH  = '/sys/block/'

def file_to_lines(fname):
    try:
        with open(fname, "r") as fd:
            return fd.readlines()
    except:
        return []

def file_to_line(fname):
    ret = file_to_lines(fname)
    if ret:
        return ret[0].strip()
    return ''

def str_to_bool(x):
    return x == '1'

def format_sectors(x):
    '''Pretty print a sector count.'''
    sectors = int(x)
    asectors = abs(sectors)

    if asectors == 0:
        return '0B'
    elif asectors < 2048:
        return '%.2fKiB' % (sectors / 2)
    elif asectors < 2097152:
        return '%.2fMiB' % (sectors / 2048)
    elif asectors < 2147483648:
        return '%.2fGiB' % (sectors / 2097152)
    else:
        return '%.2fTiB' % (sectors / 2147483648)

def interpret_sectors(x):
    '''Interpret a pretty-printed disk size.'''
    factors = {
        'k': 1 << 10,
        'M': 1 << 20,
        'G': 1 << 30,
        'T': 1 << 40,
        'P': 1 << 50,
        'E': 1 << 60,
        'Z': 1 << 70,
        'Y': 1 << 80,
    }

    if len(x)>0:
        factor = 1
        if x[-1] in factors:
            factor = factors[x[-1]]
            x = x[:-1]
        return int(float(x) * factor / 512)
    else:
        return 1

def pretty_size(x):
    return format_sectors(interpret_sectors(x))

def pretty_time(sec):
    return timedelta(seconds=int(sec))

def dump_bdev(bdev_path):
    '''Dump a backing device stats.'''
    global MAX_KEY_LENGTH, devnum_map
    attrs = [
        ('../dev',              'Device',               lambda x: '%s (%s)' % (devnum_map.get(x, '?'), x)),
        ('../size',             'Size',                 format_sectors),
        ('cache_mode',          'Cache Mode',           None),
        ('readahead',           'Readahead',            None),
        ('sequential_cutoff',   'Sequential Cutoff',    pretty_size),
        ('sequential_merge',    'Merge sequential?',    str_to_bool),
        ('state',               'State',                None),
        ('writeback_running',   'Writeback?',           str_to_bool),
        ('dirty_data',          'Dirty Data',           pretty_size),
    ]

    print('--- Backing Device ---')
    for (sysfs_name, display_name, conversion_func) in attrs:
        val = file_to_line('%s/%s' % (bdev_path, sysfs_name))
        if conversion_func is not None:
            val = conversion_func(val)
        if display_name is None:
            display_name = sysfs_name
        print('  %-*s%s' % (MAX_KEY_LENGTH - 2, display_name, val))

def dump_cachedev(cachedev_path):
    '''Dump a cachding device stats.'''
    def fmt_cachesize(val):
        return '%s\t(%d%%)' % (format_sectors(val), float(val) / cache_size * 100)

    global MAX_KEY_LENGTH, devnum_map
    attrs = [
        ('../dev',                   'Device',             lambda x: '%s (%s)' % (devnum_map.get(x, '?'), x)),
        ('../size',                  'Size',               format_sectors),
        ('block_size',               'Block Size',         pretty_size),
        ('bucket_size',              'Bucket Size',        pretty_size),
        ('cache_replacement_policy', 'Replacement Policy', None),
        ('discard',                  'Discard?',           str_to_bool),
        ('io_errors',                'I/O Errors',         None),
        ('metadata_written',         'Metadata Written',   pretty_size),
        ('written',                  'Data Written',       pretty_size),
        ('nbuckets',                 'Buckets',            None),
        (None,                       'Cache Used',         lambda x: fmt_cachesize(used_sectors)),
        (None,                       'Cache Unused',       lambda x: fmt_cachesize(unused_sectors)),
    ]

    stats = get_cache_priority_stats(cachedev_path)
    cache_size = int(file_to_line('%s/../size' % cachedev_path))
    unused_sectors = float(stats['Unused'][:-1]) * cache_size / 100
    used_sectors = cache_size - unused_sectors

    print('--- Cache Device ---')
    for (sysfs_name, display_name, conversion_func) in attrs:
        if sysfs_name is not None:
            val = file_to_line('%s/%s' % (cachedev_path, sysfs_name))
        if conversion_func is not None:
            val = conversion_func(val)
        if display_name is None:
            display_name = sysfs_name
        print('  %-*s%s' % (MAX_KEY_LENGTH - 2, display_name, val))

def hits_to_str(hits_str, misses_str):
    '''Render a hits/misses ratio as a string.'''
    hits = int(hits_str)
    misses = int(misses_str)

    ret = '%d' % hits
    if hits + misses != 0:
        ret = '%s\t(%.d%%)' % (ret, 100 * hits / (hits + misses))
    return ret

def dump_stats(sysfs_path, indent_str, stats):
    '''Dump stats on a bcache device.'''
    stat_types = [
        ('five_minute', 'Last 5min'),
        ('hour',        'Last Hour'),
        ('day',         'Last Day'),
        ('total',       'Total'),
    ]
    attrs = ['bypassed', 'cache_bypass_hits', 'cache_bypass_misses', 'cache_hits', 'cache_misses']
    display = [
        ('Hits',          lambda: hits_to_str(stat_data['cache_hits'], stat_data['cache_misses'])),
        ('Misses',        lambda: stat_data['cache_misses']),
        ('Bypass Hits',   lambda: hits_to_str(stat_data['cache_bypass_hits'], stat_data['cache_bypass_misses'])),
        ('Bypass Misses', lambda: stat_data['cache_bypass_misses']),
        ('Bypassed',      lambda: pretty_size(stat_data['bypassed'])),
    ]

    for (sysfs_name, stat_display_name) in stat_types:
        if len(stats) > 0 and sysfs_name not in stats:
            continue
        stat_data = {}
        for attr in attrs:
            val = file_to_line('%s/stats_%s/%s' % (sysfs_path, sysfs_name, attr))
            stat_data[attr] = val
        for (display_name, str_func) in display:
            d = '%s%s %s' % (indent_str, stat_display_name, display_name)
            print('%-*s%s' % (MAX_KEY_LENGTH, d, str_func()))

def get_cache_priority_stats(cache):
    '''Retrieve priority stats from a cache.'''
    attrs = {}

    for line in file_to_lines('%s/priority_stats' % cache):
        x = line.split()
        key = x[0]
        value = x[1]
        attrs[key[:-1]] = value
    return attrs

def dump_bcache(bcache_sysfs_path, stats, print_subdevices, devices):
    '''Dump bcache stats'''
    global devnum_map
    def fmt_cachesize(val):
        return '%s\t(%d%%)' % (format_sectors(val), 100.0 * val / cache_sectors)

    attrs_cache = [
        (None,                           'UUID',               lambda x: os.path.basename(bcache_sysfs_path)),
        ('block_size',                   'Block Size',         pretty_size),
        ('bucket_size',                  'Bucket Size',        pretty_size),
        ('congested',                    'Congested?',         str_to_bool),
        ('congested_read_threshold_us',  'Read Congestion',    lambda x: '%.1fms' % (int(x) / 1000)),
        ('congested_write_threshold_us', 'Write Congestion',   lambda x: '%.1fms' % (int(x) / 1000)),
        (None,                           'Total Cache Size',   lambda x: format_sectors(cache_sectors)),
        (None,                           'Total Cache Used',   lambda x: fmt_cachesize(cache_used_sectors)),
        (None,                           'Total Cache Unused', lambda x: fmt_cachesize(cache_unused_sectors)),
        ('btree_cache_size',             'BTree Cache Size',   pretty_size),
        ('cache_available_percent',      'Evictable Cache',    lambda x: '%s\t(%s%%)' % (format_sectors(float(x) * cache_sectors / 100), x)),
        (None,                           'Replacement Policy', lambda x: replacement_policies.pop() if len(replacement_policies) == 1 else '(Unknown)'),
    ]
    attrs_bdev = [
        ('dev/dev',                      'Device',             lambda x: '%s (%s)' % (devnum_map.get(x, '?'), x)),
        ('cache_mode',                   'Cache Mode',         None),
        ('dev/size',                     'Total Size',         format_sectors),
        ('dirty_data',                   'Dirty Data',         pretty_size),
        ('stripe_size',                  'Stripe Size',        pretty_size),
        ('sequential_cutoff',            'Sequential Cutoff',  pretty_size),
        ('readahead_cache_policy',       'Readahead Cache',    None),
        ('writeback_delay',              'Writeback Delay',    pretty_time),
        ('writeback_percent',            'Writeback Percent',  lambda x: '%s' % x + '%'),
        ('writeback_rate',               'Writeback rate',     lambda x: '%s sectors' % x),
    ]

    bdevs = []

    # Calculate aggregate data
    cache_name = ''
    cache_sectors = 0
    cache_unused_sectors = 0
    cache_modes = set()
    replacement_policies = set()
    for obj in os.listdir(bcache_sysfs_path):
        # print(obj)
        if not os.path.isdir('%s/%s' % (bcache_sysfs_path, obj)):
            continue
        if obj.startswith('cache'):
            cache_name = obj
            cache_size = int(file_to_line('%s/%s/../size' % (bcache_sysfs_path, obj)))
            ### print('%s/%s/../size' % (bcache_sysfs_path, obj))
            cache_sectors += cache_size
            cstats = get_cache_priority_stats('%s/%s' % (bcache_sysfs_path, obj))
            unused_size = float(cstats['Unused'][:-1]) * cache_size / 100
            cache_unused_sectors += unused_size
            replacement_policies.add(file_to_line('%s/%s/cache_replacement_policy' % (bcache_sysfs_path, obj)))
            cache_used_sectors = cache_sectors - cache_unused_sectors
        elif obj.startswith('bdev'):
            ##dump_stats('%s/%s' % (bcache_sysfs_path, obj))
            bdevs.append('%s/%s' % (bcache_sysfs_path, obj))
    bdevs.sort()

    # Dump cache stats
    print("--- %s ---" % cache_name)
    for (sysfs_name, display_name, conversion_func) in attrs_cache:
        if sysfs_name is not None:
            val = file_to_line('%s/%s' % (bcache_sysfs_path, sysfs_name))
        else:
            val = None
        if conversion_func is not None:
            val = conversion_func(val)
        if display_name is None:
            display_name = sysfs_name
        print('%-*s%s' % (MAX_KEY_LENGTH, display_name, val))
    dump_stats(bcache_sysfs_path, '', stats)

    for bdev in bdevs:
        print("--- %s ---" % os.path.basename(bdev))
        for (sysfs_name, display_name, conversion_func) in attrs_bdev:
            if sysfs_name is not None:
                val = file_to_line('%s/%s' % (bdev, sysfs_name))
            else:
                val = None
            if conversion_func is not None:
                val = conversion_func(val)
            if display_name is None:
                display_name = sysfs_name
            print('%-*s%s' % (MAX_KEY_LENGTH, display_name, val))

        dump_stats(bdev, '', stats)

    # Dump sub-device stats
    if not print_subdevices:
        return
    for obj in os.listdir(bcache_sysfs_path):
        if not os.path.isdir('%s/%s' % (bcache_sysfs_path, obj)):
            continue
        if obj.startswith('bdev'):
            dump_bdev('%s/%s' % (bcache_sysfs_path, obj))
            dump_stats('%s/%s' % (bcache_sysfs_path, obj), '  ', stats)
        elif obj.startswith('cache'):
            dump_cachedev('%s/%s' % (bcache_sysfs_path, obj))

def map_uuid_to_device():
    '''Map bcache UUIDs to device files.'''
    global SYSFS_BLOCK_PATH
    ret = {}

    for bdev in os.listdir(SYSFS_BLOCK_PATH):
        link = '%s%s/bcache/cache' % (SYSFS_BLOCK_PATH, bdev)
        if not os.path.islink(link):
            continue
        basename = os.path.basename(os.readlink(link))
        ret[basename] = file_to_line('%s%s/dev' % (SYSFS_BLOCK_PATH, bdev))
    return ret

def get_bcache_devices():
    '''Map bcache UUIDs to device files.'''
    global SYSFS_BLOCK_PATH
    blist = {}

    for bdev in os.listdir(SYSFS_BLOCK_PATH):
        link = '%s%s/bcache/cache' % (SYSFS_BLOCK_PATH, bdev)
        if not os.path.islink(link):
            continue
        basename = os.path.basename(os.readlink(link))
        blist[bdev] = basename
    return blist


def map_devnum_to_device():
    '''Map device numbers to device files.'''
    global DEV_BLOCK_PATH
    ret = {}

    for bdev in os.listdir(DEV_BLOCK_PATH):
        ret[bdev] = os.path.realpath('%s%s' % (DEV_BLOCK_PATH, bdev))
    return ret

def main():
    '''Main function'''
    global SYSFS_BCACHE_PATH
    global uuid_map, devnum_map
    stats = set()
    reset_stats = False
    print_subdevices = False
    run_gc = False

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help',              help='show this help message and exit',       action='store_true')
    parser.add_argument('-f', '--five-minute', help='Print the last five minutes of stats.', action='store_true')
    parser.add_argument('-h', '--hour',        help='Print the last hour of stats.',         action='store_true')
    parser.add_argument('-d', '--day',         help='Print the last day of stats.',          action='store_true')
    parser.add_argument('-t', '--total',       help='Print total stats.',                    action='store_true')
    parser.add_argument('-a', '--all',         help='Print all stats.',                      action='store_true')
    parser.add_argument('-r', '--reset-stats', help='Reset stats after printing them.',      action='store_true')
    parser.add_argument('-s', '--sub-status',  help='Print subdevice status.',               action='store_true')
    parser.add_argument('-g', '--gc',          help='Invoke GC before printing status.',     action='store_true')
    parser.add_argument('-R', '--repeat',      help='Run periodically.',                     action='store_true')
    parser.add_argument('-I', '--interval',    help='Update interval.',                      dest = 'interval', type = int, default = 3600)

    args = parser.parse_args()

    if args.help:
        parser.print_help()
        return 0

    if args.five_minute:
        stats.add('five_minute')
    if args.hour:
        stats.add('hour')
    if args.day:
        stats.add('day')
    if args.total:
        stats.add('total')
    if args.all:
        stats.add('five_minute')
        stats.add('hour')
        stats.add('day')
        stats.add('total')
    if args.reset_stats:
        reset_stats = True
    if args.sub_status:
        print_subdevices = True
    if args.gc:
        run_gc = True

    if not stats:
        stats.add('total')

    uuid_map = map_uuid_to_device()
    devnum_map = map_devnum_to_device()
    bcache_devices = get_bcache_devices()

    while True:

        now = datetime.now()
        print (now.strftime("============ %Y-%m-%d %H:%M:%S =============="))

        for cache in os.listdir(SYSFS_BCACHE_PATH):
            if not os.path.isdir('%s%s' % (SYSFS_BCACHE_PATH, cache)):
                continue

            devices = []
            for bcache, cset in bcache_devices.items():
                if cset == cache:
                    devices.append(bcache)

            if run_gc:
                with open('%s%s/internal/trigger_gc' % (SYSFS_BCACHE_PATH, cache), 'w') as fd:
                    fd.write('1\n')

            dump_bcache('%s%s' % (SYSFS_BCACHE_PATH, cache), stats, print_subdevices, devices)

            if reset_stats:
                with open('%s%s/clear_stats' % (SYSFS_BCACHE_PATH, cache), 'w') as fd:
                    fd.write('1\n')

        if not args.repeat:
            break

        sleep(args.interval)

if __name__ == '__main__':
    main()