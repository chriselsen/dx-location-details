#!/usr/bin/env python3
import json
import os

def merge_partitions():
    """Merge commercial and EUSC partition data into single file"""
    
    commercial_file = 'data-structures/dx-locations-data.json'
    eusc_file = 'data-structures/dx-locations-data-eusc.json'
    output_file = 'data-structures/dx-locations-data-merged.json'
    
    merged_data = []
    
    # Load commercial data
    if os.path.exists(commercial_file):
        with open(commercial_file, 'r') as f:
            commercial_data = json.load(f)
            # Add partition field to commercial data if not present
            for entry in commercial_data:
                if 'partition' not in entry:
                    entry['partition'] = 'aws'
            merged_data.extend(commercial_data)
            print(f"Loaded {len(commercial_data)} commercial locations")
    else:
        print(f"WARNING: {commercial_file} not found")
    
    # Load EUSC data
    if os.path.exists(eusc_file):
        with open(eusc_file, 'r') as f:
            eusc_data = json.load(f)
            merged_data.extend(eusc_data)
            print(f"Loaded {len(eusc_data)} EUSC locations")
    else:
        print(f"INFO: {eusc_file} not found, skipping EUSC data")
    
    # Sort by partition, then region, then code
    merged_data.sort(key=lambda x: (x.get('partition', 'aws'), x['region'], x['code']))
    
    # Save merged data
    with open(output_file, 'w') as f:
        json.dump(merged_data, f, indent=2)
    
    print(f"\nMerged {len(merged_data)} total locations to: {output_file}")
    
    # Print summary by partition
    partitions = {}
    for entry in merged_data:
        partition = entry.get('partition', 'aws')
        partitions[partition] = partitions.get(partition, 0) + 1
    
    print("\nBy partition:")
    for partition, count in sorted(partitions.items()):
        print(f"  {partition}: {count} locations")

if __name__ == '__main__':
    merge_partitions()
