#!/usr/bin/env python3
import json

# Read icon from icons/icon.txt
with open('icons/icon.txt', 'r') as f:
    ICON_DATA = f.read().strip()

def generate_kml(locations, output_file):
    """Generate KML file for China locations"""
    kml = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>AWS Direct Connect Locations - China</name>
    <description>China Direct Connect Locations</description>
    <Style id="directConnectIcon">
      <IconStyle>
        <Icon>
          <href>{ICON_DATA}</href>
        </Icon>
      </IconStyle>
    </Style>
"""
    
    for loc in locations:
        if loc.get('latitude') and loc.get('longitude'):
            kml += f"""    <Placemark>
      <name>{loc['code']}</name>
      <description>{loc['name']}</description>
      <styleUrl>#directConnectIcon</styleUrl>
      <Point>
        <coordinates>{loc['longitude']},{loc['latitude']},0</coordinates>
      </Point>
    </Placemark>
"""
    
    kml += """  </Document>
</kml>
"""
    
    with open(output_file, 'w') as f:
        f.write(kml)
    
    return len([loc for loc in locations if loc.get('latitude') and loc.get('longitude')])

def main():
    # Read China data
    with open('data-structures/dx-locations-data-china.json', 'r') as f:
        locations = json.load(f)
    
    # Generate China KML
    count = generate_kml(locations, 'output/DirectConnectLocations_CHINA.kml')
    print(f"Generated: output/DirectConnectLocations_CHINA.kml ({count} locations)")

if __name__ == '__main__':
    main()
