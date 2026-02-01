#!/usr/bin/env python3
import json
import csv

def main():
    # Read EUSC data
    with open('data-structures/dx-locations-data-eusc.json', 'r') as f:
        locations = json.load(f)
    
    # Read region mapping for region names
    with open('data-structures/region-mapping.json', 'r') as f:
        region_mapping = json.load(f)
    
    # Generate CSV
    with open('output/DX_LOCATIONS_EUSC.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'Location Code',
            'Partition',
            'Location Name',
            'AWS Name',
            'Country',
            'Region Code',
            'Region Name',
            'Port Speeds',
            'MACsec Capable',
            'PeeringDB ID',
            'Latitude',
            'Longitude'
        ])
        
        # Data rows
        for loc in sorted(locations, key=lambda x: (x['region'], x['code'])):
            region_name = region_mapping.get('aws_region_names', {}).get(loc['region'], loc['region'])
            
            writer.writerow([
                loc['code'],
                loc.get('partition', 'aws-eusc'),
                loc['name'],
                loc.get('aws_name', ''),
                loc.get('country', ''),
                loc['region'],
                region_name,
                ', '.join(loc.get('port_speeds', [])),
                ', '.join(loc.get('macsec_capable', [])),
                loc.get('peeringdb_id', ''),
                loc.get('latitude', ''),
                loc.get('longitude', '')
            ])
    
    print(f"CSV file generated: output/DX_LOCATIONS_EUSC.csv")

if __name__ == '__main__':
    main()
