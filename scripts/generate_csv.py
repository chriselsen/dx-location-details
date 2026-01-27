#!/usr/bin/env python3
import json
import csv

def main():
    with open('data-structures/dx-locations-data.json', 'r') as f:
        data = json.load(f)
    
    with open('data-structures/region-mapping.json', 'r') as f:
        regions = json.load(f)
    
    with open('output/DX_LOCATIONS.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Location Code', 'Location Name', 'Country', 'Region Code', 'Region Name', 
                        'Port Speeds', 'MACsec Capable', 'PeeringDB ID', 'Latitude', 'Longitude'])
        
        for loc in sorted(data, key=lambda x: (x['region'], x['name'])):
            region_name = regions.get(loc['region'], {}).get('name', loc['region'])
            port_speeds = ', '.join(loc.get('port_speeds', []))
            macsec = ', '.join(loc.get('macsec_capable', []))
            
            writer.writerow([
                loc['code'],
                loc['name'],
                loc.get('country', ''),
                loc['region'],
                region_name,
                port_speeds,
                macsec,
                loc.get('peeringdb_id', ''),
                loc.get('latitude', ''),
                loc.get('longitude', '')
            ])
    
    print("CSV file generated: output/DX_LOCATIONS.csv")

if __name__ == '__main__':
    main()
