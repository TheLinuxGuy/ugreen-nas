# Function to extract bandwidth value from FIO output - simplified version
extract_bandwidth() {
    local file=$1
    local op=$2  # read or write
    
    # Extract just the main bandwidth value with units
    local bw_line=$(grep -A2 "Run status group 0" "$file" | grep -i "$op:" | head -1)
    local bw=$(echo "$bw_line" | awk '{
        for(i=1;i<=NF;i++) {
            if($i ~ /bw=/) {
                print $(i+1);
                exit;
            }
        }
    }')
    
    if [ -z "$bw" ]; then
        # Try alternative format - extract just the first measurement
        bw=$(echo "$bw_line" | awk '{
            for(i=1;i<=NF;i++) {
                if($i ~ /[0-9]+(\.[0-9]+)?(KiB|MiB|GiB)\/s/) {
                    print $i;
                    exit;
                }
            }
        }')
    fi
    
    echo "$bw"
}

# Function to extract latency value from FIO output - without colon
extract_latency() {
    local file=$1
    local op=$2  # read or write
    
    # Extract average latency without trailing colon
    local lat_line=$(grep -i "^ *$op:" -A10 "$file" | grep " lat " | grep -v "percentiles" | head -1)
    local lat=$(echo "$lat_line" | awk -F 'avg=' '{print $2}' | awk -F ',' '{print $1}')
    local unit=$(echo "$lat_line" | awk '{print $2}' | sed 's/[()]//g')
    
    if [ -n "$lat" ] && [ -n "$unit" ]; then
        echo "$lat $unit"
    else
        echo "N/A"
    fi
}

# Function to display a summary table with fixed column widths
display_summary_table() {
    echo "+----------------------+---------------+---------------+---------------+"
    echo "| Test                 | IOPS          | Bandwidth     | Latency (avg) |"
    echo "+----------------------+---------------+---------------+---------------+"
    
    # Process each test result
    for test in write_throughput write_iops read_throughput read_iops; do
        if [[ -f "$RESULTS_DIR/${test}.txt" ]]; then
            local op=""
            if [[ "$test" == *"write"* ]]; then
                op="write"
            else
                op="read"
            fi
            
            local iops=$(extract_iops "$RESULTS_DIR/${test}.txt" "$op")
            local bw=$(extract_bandwidth "$RESULTS_DIR/${test}.txt" "$op")
            local lat=$(extract_latency "$RESULTS_DIR/${test}.txt" "$op")
            
            printf "| %-20s | %-13s | %-13s | %-13s |\n" "$test" "$iops" "$bw" "$lat"
        fi
    done
    
    echo "+----------------------+---------------+---------------+---------------+"
}
