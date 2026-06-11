#!/usr/bin/env python3
"""Generate docs/locations.json - a machine-readable version of all DX locations for AI crawlers.

Strips internal-only fields and writes to docs/locations.json for machine consumption.
Includes a metadata envelope with field descriptions.
"""
import json
from datetime import datetime, timezone

def main():
    # Use merged data if available, otherwise fall back to commercial only
    try:
        with open('data-structures/dx-locations-data-merged.json', 'r', encoding='utf-8') as f:
            locations = json.load(f)
    except FileNotFoundError:
        with open('data-structures/dx-locations-data.json', 'r', encoding='utf-8') as f:
            locations = json.load(f)

    # Build clean machine-readable output
    public_locations = []
    for loc in locations:
        clean = {k: v for k, v in loc.items()}
        public_locations.append(clean)

    output = {
        "description": "AWS Direct Connect colocation facility locations across all AWS partitions.",
        "source": "https://github.com/chriselsen/dx-location-details",
        "last_updated": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        "fields": {
            "code": "AWS Direct Connect location code (used in API calls)",
            "region": "AWS region code for managing Direct Connect resources at this location",
            "region_opt_status": "Whether the region requires opt-in (ENABLED_BY_DEFAULT or ENABLED)",
            "name": "Facility name and city from PeeringDB",
            "aws_name": "AWS marketing name for this location",
            "peeringdb_id": "PeeringDB facility ID (https://www.peeringdb.com/fac/{id})",
            "org_id": "PeeringDB organization ID (https://www.peeringdb.com/org/{id})",
            "org_name": "Colocation provider / facility operator name from PeeringDB",
            "country": "ISO 3166-1 alpha-2 country code",
            "latitude": "Facility latitude (decimal degrees)",
            "longitude": "Facility longitude (decimal degrees)",
            "port_speeds": "Available port speed options (e.g. 1G, 10G, 100G, 400G)",
            "macsec_capable": "Port speeds that support MACsec encryption",
            "providers": "AWS Direct Connect Partners available at this location",
            "carriers": "Network carriers present at the facility (from PeeringDB)",
            "campus": "PeeringDB campus info if facility is part of a multi-building campus",
            "partition": "AWS partition (aws, aws-govcloud, aws-cn, aws-eusc)"
        },
        "locations": public_locations
    }

    with open('docs/locations.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write('\n')

    print(f"Generated docs/locations.json ({len(public_locations)} locations)")

if __name__ == '__main__':
    main()
