#!/bin/bash
# Disable ZFS caching to benchmark performance
# This script sets a temporary ARC size, runs a benchmark using FIO,
# and restores the original ARC size afterwards.

# TheLinuxGuy 07/28/2025
# Usage: ./zfs-benchmark.sh <POOL> <TEST_DIR>
# Example: ./zfs-benchmark.sh rpool /rpool/benchmark/

set -euo pipefail

# ================
# Configuration
# ================

# ARC size to use for benchmark
ARC_TMP=268435456  # 256 MB

# Benchmark parameters
FIO_RUNTIME=60      # Time per test
FIO_SIZE=2G         # Total file size per job
FIO_JOBS=4          # Number of parallel jobs
FIO_IODEPTH=16      # Queue depth

# ========================
# Parse Arguments
# ========================
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <POOL_NAME> <TEST_DIR>"
    exit 1
fi

POOL="$1"
TEST_DIR="$2"

# ========================
# Save current ARC config
# ========================
ZFS_ARC_MAX_FILE="/sys/module/zfs/parameters/zfs_arc_max"
ZFS_ARC_MAX_OLD=$(cat "$ZFS_ARC_MAX_FILE")

# ========================
# Trap cleanup on exit
# ========================
function restore_arc {
    echo "Restoring original ARC max value..."
    echo $ZFS_ARC_MAX_OLD | sudo tee "$ZFS_ARC_MAX_FILE" > /dev/null
    echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
}
trap restore_arc EXIT

# ========================
# Benchmark Functions
# ========================

function disable_arc {
    echo "Disabling ARC (setting max to 256MB)..."
    echo $ARC_TMP | sudo tee "$ZFS_ARC_MAX_FILE" > /dev/null
    echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null
}

function setup {
    echo "Creating test directory: $TEST_DIR"
    sudo mkdir -p "$TEST_DIR"
    sudo chown $USER "$TEST_DIR"
}

function cleanup {
    echo "Cleaning up test files..."
    sudo rm -rf "$TEST_DIR"
}

function run_fio {
    echo "Running FIO benchmark on $TEST_DIR..."
    fio --name=zfs-benchmark \
        --directory="$TEST_DIR" \
        --rw=randrw \
        --bs=4k \
        --size=$FIO_SIZE \
        --numjobs=$FIO_JOBS \
        --iodepth=$FIO_IODEPTH \
        --runtime=$FIO_RUNTIME \
        --time_based \
        --group_reporting
}

# ========================
# Main
# ========================
setup
disable_arc
run_fio
cleanup