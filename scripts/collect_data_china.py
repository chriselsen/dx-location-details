#!/usr/bin/env python3
import json
import subprocess
import re
import os
import sys
from collections import defaultdict

AWS_PROFILE = os.environ.get('AWS_PROFILE', '')
if len(sys.argv) > 1:
    AWS_PROFILE = sys.argv[1]

def load_mapping(mapping_file):
    with open(mapping_file, 'r') as f:
        return json.load(f)

def normalize_location_code(code):
    """Remove floor suffixes like -32FL, -10FL and MMR suffixes, normalize case"""
    code = re.sub(r'-\d+FL$', '', code)
    code = re.sub(r'-MMR-\w+$', '', code)
    code = re.sub(r'-(\d{5}|CDLAN-[AB]|MIX-DC\d+|SC\d+|EQ|WBE|MMRA|MMRB|MMR\d+|CM|CT|CU|OTHER)$', '', code)
    return code.upper()

def get_china_regions():
    """Fetch China regions dynamically using ec2:DescribeRegions"""
    profile_arg = f"--profile {AWS_PROFILE}" if AWS_PROFILE else ""
    cmd = f"aws ec2 describe-regions {profile_arg} --region cn-north-1 --query 'Regions[*].RegionName' --output json"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error fetching regions: {result.stderr}")
        return []
    
    return json.loads(result.stdout)

def get_dx_locations():
    """Fetch DX locations from all China regions"""
    regions = get_china_regions()
    print(f"Found {len(regions)} China regions: {', '.join(regions)}")
    
    profile_arg = f"--profile {AWS_PROFILE}" if AWS_PROFILE else ""
    
    all_lines = []
    for region in regions:
        cmd = f"aws directconnect describe-locations --region {region} {profile_arg} --query 'locations[]' --no-cli-pager --output text"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, executable='/bin/bash')
        if result.stdout.strip():
            all_lines.extend(result.stdout.strip().split('\n'))
    
    return all_lines

def normalize_country_from_name(name, country_mapping):
    """Extract and normalize country from location name"""
    parts = [p.strip() for p in name.split(',')]
    if len(parts) >= 2:
        country = parts[-1]
        if country in country_mapping:
            return country_mapping[country]
        if len(country) == 2 and country.isupper():
            return country
    return None

def extract_aws_name(aws_full_name):
    """Extract AWS name without city/country (everything before first comma)"""
    return aws_full_name.split(',')[0].strip()

def build_peeringdb_name(peeringdb_facility_name, map_data):
    """Build PeeringDB name: Facility Name (first part), City, State, Country"""
    facility_name = peeringdb_facility_name.split(',')[0].strip() if peeringdb_facility_name else None
    
    if not facility_name:
        return None
    
    parts = [facility_name]
    
    if map_data.get('city'):
        parts.append(map_data['city'])
    
    if map_data.get('state'):
        parts.append(map_data['state'])
    
    if map_data.get('country'):
        parts.append(map_data['country'])
    
    return ', '.join(parts)

def sort_port_speeds(speeds):
    """Sort port speeds in ascending order"""
    order = {'50M': 0, '100M': 1, '200M': 2, '300M': 3, '400M': 4, '500M': 5, 
             '1G': 6, '2G': 7, '5G': 8, '10G': 9, '100G': 10}
    return sorted(speeds, key=lambda x: order.get(x, 999))

def parse_locations(lines):
    """Parse location data and deduplicate by normalized code"""
    locations = defaultdict(lambda: {'region': None, 'name': None, 'port_speeds': set(), 'macsec_speeds': set()})
    current_code = None
    
    for line in lines:
        if not line.strip():
            continue
        parts = line.split('\t')
        
        if len(parts) >= 3 and not parts[0].startswith('AVAILABLE'):
            code, name, region = parts[0], parts[1], parts[2]
            current_code = normalize_location_code(code)
            if not locations[current_code]['region']:
                locations[current_code]['region'] = region
                locations[current_code]['name'] = name
        elif len(parts) >= 2 and current_code:
            if parts[0] == 'AVAILABLEPORTSPEEDS':
                locations[current_code]['port_speeds'].add(parts[1])
            elif parts[0] == 'AVAILABLEMACSECPORTSPEEDS':
                locations[current_code]['macsec_speeds'].add(parts[1])
    
    for code in locations:
        locations[code]['port_speeds'] = sort_port_speeds(list(locations[code]['port_speeds']))
        locations[code]['macsec_speeds'] = sort_port_speeds(list(locations[code]['macsec_speeds']))
    
    return locations

def main():
    mapping_file = 'data-structures/location-mapping.json'
    country_mapping_file = 'data-structures/country-mapping.json'
    output_file = 'data-structures/dx-locations-data-china.json'
    
    print("Loading mappings...")
    mapping = load_mapping(mapping_file)
    country_mapping = load_mapping(country_mapping_file)
    
    print("Fetching DX locations from China...")
    lines = get_dx_locations()
    
    print("Parsing locations...")
    locations = parse_locations(lines)
    
    print(f"Found {len(locations)} unique China locations")
    
    complete_data = []
    missing_locations = []
    
    for code, data in sorted(locations.items(), key=lambda x: (x[1]['region'], x[0])):
        region = data['region']
        aws_name = data['name']
        port_speeds = data['port_speeds']
        macsec_speeds = data['macsec_speeds']
        
        entry = {
            'code': code,
            'partition': 'aws-cn',
            'region': region,
            'name': None,
            'aws_name': extract_aws_name(aws_name),
            'internal_code': None,
            'peeringdb_id': None,
            'org_id': None,
            'org_name': None,
            'country': None,
            'latitude': None,
            'longitude': None,
            'ip': None,
            'port_speeds': port_speeds,
            'macsec_capable': macsec_speeds
        }
        
        if code in mapping:
            map_data = mapping[code]
            entry['peeringdb_id'] = map_data.get('peeringdb_id')
            entry['org_id'] = map_data.get('org_id')
            entry['org_name'] = map_data.get('org_name')
            entry['country'] = map_data.get('country')
            
            if 'coordinates' in map_data:
                entry['latitude'] = map_data['coordinates']['lat']
                entry['longitude'] = map_data['coordinates']['lon']
            
            if map_data.get('facility_name'):
                entry['name'] = build_peeringdb_name(map_data['facility_name'], map_data)
            
            if not entry['name']:
                entry['name'] = entry['aws_name']
        else:
            missing_locations.append({'code': code, 'name': aws_name, 'region': region})
        
        if not entry['country']:
            entry['country'] = normalize_country_from_name(aws_name, country_mapping)
        
        complete_data.append(entry)
    
    if missing_locations:
        print(f"\nWARNING: Found {len(missing_locations)} China location(s) without mapping:")
        for loc in missing_locations:
            print(f"  - {loc['code']}: {loc['name']} (Region: {loc['region']})")
        print(f"\nYou can add these locations using: python3 scripts/add_location.py")
    
    with open(output_file, 'w') as f:
        json.dump(complete_data, f, indent=2)
    
    print(f"\nChina data saved to: {output_file}")
    
    total = len(complete_data)
    with_mapping = sum(1 for e in complete_data if e['peeringdb_id'])
    with_coords = sum(1 for e in complete_data if e['latitude'])
    
    print(f"\nSummary:")
    print(f"  Total China locations: {total}")
    print(f"  With mapping: {with_mapping}")
    print(f"  With coordinates: {with_coords}")
    print(f"  Missing mapping: {total - with_mapping}")

if __name__ == '__main__':
    main()
