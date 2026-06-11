#!/usr/bin/env python3
import json
import os

# Known opt-in regions (must be explicitly enabled in AWS account)
OPT_IN_REGIONS = {
    'af-south-1', 'ap-east-1', 'ap-east-2', 'ap-southeast-3', 'ap-southeast-4',
    'ap-southeast-5', 'ap-southeast-6', 'ap-southeast-7', 'ca-west-1',
    'eu-central-2', 'eu-south-1', 'eu-south-2', 'il-central-1', 'mx-central-1',
}

def merge_partitions():
    """Merge commercial, EUSC, and China partition data into single file"""
    
    commercial_file = 'data-structures/dx-locations-data.json'
    eusc_file = 'data-structures/dx-locations-data-eusc.json'
    china_file = 'data-structures/dx-locations-data-china.json'
    mapping_file = 'data-structures/location-mapping.json'
    output_file = 'data-structures/dx-locations-data-merged.json'
    
    # Load location mapping for enrichment
    mapping = {}
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r') as f:
            mapping = json.load(f)
    
    merged_data = []
    
    # Load commercial data
    if os.path.exists(commercial_file):
        with open(commercial_file, 'r') as f:
            commercial_data = json.load(f)
            for entry in commercial_data:
                if 'partition' not in entry:
                    entry['partition'] = 'aws'
                # Enrich with org data from mapping if missing
                code = entry.get('code', '')
                if code in mapping:
                    map_data = mapping[code]
                    if not entry.get('org_id') and map_data.get('org_id'):
                        entry['org_id'] = map_data['org_id']
                    if not entry.get('org_name') and map_data.get('org_name'):
                        entry['org_name'] = map_data['org_name']
                    if not entry.get('campus') and map_data.get('campus'):
                        entry['campus'] = map_data['campus']
                    if not entry.get('carriers') and map_data.get('carriers'):
                        entry['carriers'] = map_data['carriers']
                # Enrich with region opt-in status if missing
                if not entry.get('region_opt_status'):
                    region = entry.get('region', '')
                    entry['region_opt_status'] = 'ENABLED' if region in OPT_IN_REGIONS else 'ENABLED_BY_DEFAULT'
            merged_data.extend(commercial_data)
            print(f"Loaded {len(commercial_data)} commercial locations")
    else:
        print(f"WARNING: {commercial_file} not found")
    
    # Load EUSC data
    if os.path.exists(eusc_file):
        with open(eusc_file, 'r') as f:
            eusc_data = json.load(f)
            for entry in eusc_data:
                code = entry.get('code', '')
                if code in mapping:
                    map_data = mapping[code]
                    if not entry.get('latitude') and 'coordinates' in map_data:
                        entry['latitude'] = map_data['coordinates']['lat']
                        entry['longitude'] = map_data['coordinates']['lon']
                    if not entry.get('org_id') and map_data.get('org_id'):
                        entry['org_id'] = map_data['org_id']
                    if not entry.get('org_name') and map_data.get('org_name'):
                        entry['org_name'] = map_data['org_name']
                    if not entry.get('country') and map_data.get('country'):
                        entry['country'] = map_data['country']
                    if not entry.get('campus') and map_data.get('campus'):
                        entry['campus'] = map_data['campus']
                    if not entry.get('carriers') and map_data.get('carriers'):
                        entry['carriers'] = map_data['carriers']
            merged_data.extend(eusc_data)
            print(f"Loaded {len(eusc_data)} EUSC locations")
    else:
        print(f"INFO: {eusc_file} not found, skipping EUSC data")
    
    # Load China data
    if os.path.exists(china_file):
        with open(china_file, 'r') as f:
            china_data = json.load(f)
            for entry in china_data:
                code = entry.get('code', '')
                if code in mapping:
                    map_data = mapping[code]
                    if not entry.get('latitude') and 'coordinates' in map_data:
                        entry['latitude'] = map_data['coordinates']['lat']
                        entry['longitude'] = map_data['coordinates']['lon']
                    if not entry.get('org_id') and map_data.get('org_id'):
                        entry['org_id'] = map_data['org_id']
                    if not entry.get('org_name') and map_data.get('org_name'):
                        entry['org_name'] = map_data['org_name']
                    if not entry.get('country') and map_data.get('country'):
                        entry['country'] = map_data['country']
                    if not entry.get('campus') and map_data.get('campus'):
                        entry['campus'] = map_data['campus']
                    if not entry.get('carriers') and map_data.get('carriers'):
                        entry['carriers'] = map_data['carriers']
            merged_data.extend(china_data)
            print(f"Loaded {len(china_data)} China locations")
    else:
        print(f"INFO: {china_file} not found, skipping China data")
    
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
