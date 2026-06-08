#!/usr/bin/env python3
"""Generate docs/locations.json - a machine-readable version of all DX locations for AI crawlers."""
import json
from datetime import datetime, timezone

def main():
    # Use merged data if available, otherwise fall back to commercial only
    try:
        with open('data-structures/dx-locations-data-merged.json', 'r') as f:
            locations = json.load(f)
    except FileNotFoundError:
        with open('data-structures/dx-locations-data.json', 'r') as f:
            locations = json.load(f)

    with open('data-structures/region-mapping.json', 'r') as f:
        region_mapping = json.load(f)

    # Build clean machine-readable output
    output_locations = []
    for loc in sorted(locations, key=lambda x: (x.get('partition', 'aws'), x['region'], x['code'])):
        region_name = region_mapping.get('aws_region_names', {}).get(loc['region'], loc['region'])

        entry = {
            'code': loc['code'],
            'partition': loc.get('partition', 'aws'),
            'name': loc.get('name'),
            'aws_name': loc.get('aws_name'),
            'organization': loc.get('org_name'),
            'country': loc.get('country'),
            'region': loc['region'],
            'region_name': region_name,
            'latitude': loc.get('latitude'),
            'longitude': loc.get('longitude'),
            'port_speeds': loc.get('port_speeds', []),
            'macsec_capable': loc.get('macsec_capable', []),
            'providers': loc.get('providers', []),
            'peeringdb_id': loc.get('peeringdb_id'),
        }
        output_locations.append(entry)

    output = {
        'metadata': {
            'description': 'AWS Direct Connect Locations',
            'source': 'https://github.com/chriselsen/dx-location-details',
            'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'total_locations': len(output_locations),
        },
        'locations': output_locations,
    }

    with open('docs/locations.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Generated docs/locations.json ({len(output_locations)} locations)")

if __name__ == '__main__':
    main()
