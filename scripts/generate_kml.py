#!/usr/bin/env python3
import json

# Read icon from icons/icon.txt
with open('icons/icon.txt', 'r') as f:
    ICON_DATA = f.read().strip()

REGION_MAP = {
    'APAC': ['ap-', 'cn-'],
    'EMEA': ['eu-', 'me-', 'af-', 'il-'],
    'NA': ['us-', 'ca-'],
    'SA': ['sa-', 'mx-']
}

def get_region(aws_region):
    for region, prefixes in REGION_MAP.items():
        for prefix in prefixes:
            if aws_region.startswith(prefix):
                return region
    return 'OTHER'

def generate_kml(locations, filename):
    kml = ['<?xml version="1.0" encoding="UTF-8"?>']
    kml.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
    kml.append('<Document>')
    kml.append('  <name>AWS Direct Connect Locations</name>')
    kml.append('  <Style id="dx-location">')
    kml.append('    <IconStyle>')
    kml.append(f'      <Icon><href>{ICON_DATA}</href></Icon>')
    kml.append('      <scale>0.8</scale>')
    kml.append('    </IconStyle>')
    kml.append('  </Style>')
    
    for loc in locations:
        lat = loc['latitude']
        lon = loc['longitude']
        code = loc['code']
        name = loc['name']
        region = loc['region']
        
        kml.append('  <Placemark>')
        kml.append(f'    <name>{code}</name>')
        kml.append(f'    <description><![CDATA[')
        kml.append(f'      <b>{name}</b><br/>')
        kml.append(f'      Region: {region}')
        kml.append(f'    ]]></description>')
        kml.append('    <styleUrl>#dx-location</styleUrl>')
        kml.append(f'    <Point><coordinates>{lon},{lat},0</coordinates></Point>')
        kml.append('  </Placemark>')
    
    kml.append('</Document>')
    kml.append('</kml>')
    
    with open(filename, 'w') as f:
        f.write('\n'.join(kml))

def main():
    with open('data-structures/dx-locations-data.json', 'r') as f:
        locations = json.load(f)
    
    # Filter locations with coordinates
    valid_locations = [loc for loc in locations if loc.get('latitude') and loc.get('longitude')]
    
    # Generate main KML
    generate_kml(valid_locations, 'output/DirectConnectLocations.kml')
    print(f"Generated: output/DirectConnectLocations.kml ({len(valid_locations)} locations)")
    
    # Generate regional KMLs
    for region in ['APAC', 'EMEA', 'NA', 'SA']:
        regional_locs = [loc for loc in valid_locations if get_region(loc['region']) == region]
        if regional_locs:
            filename = f'output/DirectConnectLocations_{region}.kml'
            generate_kml(regional_locs, filename)
            print(f"Generated: {filename} ({len(regional_locs)} locations)")

if __name__ == '__main__':
    main()
