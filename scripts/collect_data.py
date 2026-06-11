#!/usr/bin/env python3
import json
import re
import boto3
from collections import defaultdict

def load_mapping(mapping_file):
    with open(mapping_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_location_code(code):
    """Remove floor suffixes like -32FL, -10FL and MMR suffixes, normalize case"""
    code = re.sub(r'-\d+FL$', '', code)
    code = re.sub(r'-MMR-\w+$', '', code)
    code = re.sub(r'-(\d{5}|CDLAN-[AB]|MIX-DC\d+|SC\d+|EQ|WBE)$', '', code)
    return code.upper()

def get_enabled_regions():
    """Get all enabled regions using boto3, returns dict of region -> opt status"""
    client = boto3.client('account', region_name='us-east-1')
    regions = {}
    paginator = client.get_paginator('list_regions')
    for page in paginator.paginate(RegionOptStatusContains=['ENABLED', 'ENABLED_BY_DEFAULT']):
        for r in page['Regions']:
            regions[r['RegionName']] = r['RegionOptStatus']
    return regions

def get_dx_locations(regions):
    """Fetch DX locations from all regions using boto3"""
    all_locations = []
    for region in regions:
        try:
            client = boto3.client('directconnect', region_name=region)
            response = client.describe_locations()
            for loc in response.get('locations', []):
                loc['_region'] = region
                all_locations.append(loc)
        except Exception as e:
            print(f"  WARNING: Skipped {region} ({e})")
    return all_locations

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

def build_location_name(peeringdb_facility_name, map_data):
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

def extract_aws_name(aws_full_name):
    """Extract AWS name without city/country (everything before first comma)"""
    return aws_full_name.split(',')[0].strip()

def sort_port_speeds(speeds):
    """Sort port speeds in ascending order"""
    order = {'50M': 0, '100M': 1, '200M': 2, '300M': 3, '400M': 4, '500M': 5, 
             '1G': 6, '2G': 7, '5G': 8, '10G': 9, '100G': 10}
    return sorted(speeds, key=lambda x: order.get(x, 999))

# Provider name aliases for normalization
PROVIDER_ALIASES = {
    'AT&T Inc': 'AT&T',
    'Equinix Inc.': 'Equinix',
    'Equinix, Inc': 'Equinix',
    'Equinix, Inc.': 'Equinix',
    'Equinix, INc.': 'Equinix',
    'COLT': 'Colt',
    'Colt Networks': 'Colt',
    'Colt Technology Services AG': 'Colt',
    'Zayo Group': 'Zayo',
    'zayo': 'Zayo',
    'CenturyLink': 'Lumen',
    'CenturyLink / Lumen': 'Lumen',
    'Century Link / Lumen': 'Lumen',
    'AARnet': 'AARNet',
    'Bell Cananda': 'Bell Canada',
    'Coresite': 'CoreSite',
    'COX': 'Cox',
    'Cox Business': 'Cox',
    'euNetworks': 'EUNetworks',
    'Exa': 'EXA',
    'Flo Networks': 'FLO Networks',
    'Orange Business Services': 'Orange Business',
    'iXSforAll, Inc': 'iXSforAll',
    'CITIC Telecom International CPC Limited': 'CITIC Telecom CPC',
    'Cogent Communication': 'Cogent Communications',
    'Cogent': 'Cogent Communications',
    'Telecom Italia Sparke': 'Telecom Italia Sparkle',
    'Singapore Telecom LTD': 'Singtel',
    'Singapore Telecom': 'Singtel',
    'Beanfield Metro': 'Beanfield Metro',
    'Beanfield Metroconnect': 'Beanfield Metro',
    'Comcast Business': 'Comcast',
    'CrownCastle': 'Crown Castle',
    'NTT Communications Corporation': 'NTT Communications',
    'NTT Communications ICT Solutions': 'NTT Communications',
}

# Prefix-based normalization: all names starting with these prefixes map to the canonical name
PROVIDER_PREFIX_ALIASES = {
    'China Telecom': 'China Telecom',
    'China Unicom': 'China Unicom',
}

def normalize_provider(name):
    """Normalize provider name: strip whitespace, apply alias mapping, strip common suffixes."""
    name = name.strip()
    # Apply explicit alias mapping first
    if name in PROVIDER_ALIASES:
        return PROVIDER_ALIASES[name]
    # Strip common corporate suffixes (case-insensitive), loop to handle compound suffixes like "Pty Ltd"
    pattern = r',?\s*\b(Sdn Bhd|Sdn Bh|Berhad|Limited|Inc\.?|AG|GmbH|Ltd\.?|ltd\.?|SA de CV|S\.?A\.?\s*de\s*C\.?V\.?|SPA|S\.?p\.?A\.?|Pty|Corp\.?)\s*$'
    prev = None
    while prev != name:
        prev = name
        name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
    # Re-check alias mapping after suffix stripping
    if name in PROVIDER_ALIASES:
        return PROVIDER_ALIASES[name]
    # Apply prefix-based normalization
    for prefix, canonical in PROVIDER_PREFIX_ALIASES.items():
        if name.startswith(prefix):
            return canonical
    return name

def parse_locations(raw_locations):
    """Deduplicate locations by normalized code"""
    locations = defaultdict(lambda: {'region': None, 'name': None, 'port_speeds': set(), 'macsec_speeds': set(), 'providers': set()})
    
    for loc in raw_locations:
        code = normalize_location_code(loc['locationCode'])
        if not locations[code]['region']:
            locations[code]['region'] = loc['_region']
            locations[code]['name'] = loc.get('locationName', '')
        for speed in loc.get('availablePortSpeeds', []):
            locations[code]['port_speeds'].add(speed)
        for speed in loc.get('availableMacSecPortSpeeds', []):
            locations[code]['macsec_speeds'].add(speed)
        for provider in loc.get('availableProviders', []):
            normalized = normalize_provider(provider)
            if normalized:
                locations[code]['providers'].add(normalized)
    
    for code in locations:
        locations[code]['port_speeds'] = sort_port_speeds(list(locations[code]['port_speeds']))
        locations[code]['macsec_speeds'] = sort_port_speeds(list(locations[code]['macsec_speeds']))
        locations[code]['providers'] = sorted(list(locations[code]['providers']))
    
    return locations

def main():
    mapping_file = 'data-structures/location-mapping.json'
    country_mapping_file = 'data-structures/country-mapping.json'
    output_file = 'data-structures/dx-locations-data.json'
    
    print("Loading mappings...")
    mapping = load_mapping(mapping_file)
    country_mapping = load_mapping(country_mapping_file)
    
    print("Fetching enabled regions...")
    region_opt_status = get_enabled_regions()
    regions = sorted(region_opt_status.keys())
    print(f"Found {len(regions)} enabled regions")
    
    print("Fetching DX locations from AWS...")
    raw_locations = get_dx_locations(regions)
    
    print("Parsing locations...")
    locations = parse_locations(raw_locations)
    
    print(f"Found {len(locations)} unique locations")
    
    # Build complete data structure
    complete_data = []
    missing_locations = []
    
    for code, data in sorted(locations.items(), key=lambda x: (x[1]['region'], x[0])):
        region = data['region']
        aws_name = data['name']
        port_speeds = data['port_speeds']
        macsec_speeds = data['macsec_speeds']
        providers = data['providers']
        
        entry = {
            'code': code,
            'region': region,
            'region_opt_status': region_opt_status.get(region, 'UNKNOWN'),
            'name': None,
            'aws_name': extract_aws_name(aws_name),
            'peeringdb_id': None,
            'org_id': None,
            'org_name': None,
            'country': None,
            'latitude': None,
            'longitude': None,
            'port_speeds': port_speeds,
            'macsec_capable': macsec_speeds,
            'providers': providers
        }
        
        if code in mapping:
            map_data = mapping[code]
            entry['peeringdb_id'] = map_data.get('peeringdb_id')
            entry['org_id'] = map_data.get('org_id')
            entry['org_name'] = map_data.get('org_name')
            entry['country'] = map_data.get('country')
            
            # Use coordinates from mapping if available
            if 'coordinates' in map_data:
                entry['latitude'] = map_data['coordinates']['lat']
                entry['longitude'] = map_data['coordinates']['lon']
            
            # Build PeeringDB name if facility name available
            if map_data.get('facility_name'):
                entry['name'] = build_location_name(map_data['facility_name'], map_data)
            
            # Fallback to AWS name if no PeeringDB name
            if not entry['name']:
                entry['name'] = entry['aws_name']
            
            # Campus data from PeeringDB
            if map_data.get('campus'):
                entry['campus'] = map_data['campus']
            
            # Carrier data from PeeringDB
            if map_data.get('carriers'):
                entry['carriers'] = map_data['carriers']
        else:
            missing_locations.append({'code': code, 'name': aws_name, 'region': region})
        
        # Normalize country from AWS name if not in mapping
        if not entry['country']:
            entry['country'] = normalize_country_from_name(aws_name, country_mapping)
        
        complete_data.append(entry)
    
    # Check for missing locations and fail if any found
    if missing_locations:
        print(f"\nERROR: Found {len(missing_locations)} location(s) without mapping:")
        for loc in missing_locations:
            print(f"  - {loc['code']}: {loc['name']} (Region: {loc['region']})")
        print(f"\nPlease add these locations using: python3 scripts/add_location.py")
        exit(1)
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(complete_data, f, indent=2)
    
    print(f"\nData saved to: {output_file}")
    
    # Print summary
    total = len(complete_data)
    with_mapping = sum(1 for e in complete_data if e['peeringdb_id'])
    with_coords = sum(1 for e in complete_data if e['latitude'])
    
    print(f"\nSummary:")
    print(f"  Total locations: {total}")
    print(f"  With mapping: {with_mapping}")
    print(f"  With coordinates: {with_coords}")
    print(f"  Missing mapping: {total - with_mapping}")

if __name__ == '__main__':
    main()
