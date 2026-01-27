#!/usr/bin/env python3
import json
import requests
import time

def get_peeringdb_info(peeringdb_id):
    """Fetch facility info from PeeringDB API"""
    try:
        time.sleep(0.5)  # Rate limiting
        url = f"https://www.peeringdb.com/api/fac/{peeringdb_id}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                fac = data['data'][0]
                return {
                    'name': fac.get('name'),
                    'city': fac.get('city'),
                    'latitude': fac.get('latitude'),
                    'longitude': fac.get('longitude'),
                    'country': fac.get('country')
                }
        elif response.status_code == 429:
            print("Rate limited, waiting...")
            time.sleep(2)
            return get_peeringdb_info(peeringdb_id)
    except Exception as e:
        print(f"Error fetching PeeringDB: {e}")
    return None

def main():
    mapping_file = 'data-structures/location-mapping.json'
    
    # Load existing mapping
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
    
    print("=== Add New DX Location ===\n")
    
    # Get input
    code = input("Location code (e.g., TCCBK): ").strip().upper()
    if not code:
        print("Error: Code is required")
        return
    
    if code in mapping:
        print(f"Warning: {code} already exists in mapping")
        overwrite = input("Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            return
    
    peeringdb_id = input("PeeringDB ID (or press Enter to skip): ").strip()
    
    # Create entry
    entry = {
        "peeringdb_id": peeringdb_id if peeringdb_id else None
    }
    
    # Fetch from PeeringDB if ID provided
    if peeringdb_id:
        print(f"\nFetching info from PeeringDB ID {peeringdb_id}...")
        info = get_peeringdb_info(peeringdb_id)
        if info:
            print(f"  Name: {info['name']}")
            print(f"  City: {info['city']}")
            print(f"  Country: {info['country']}")
            print(f"  Coordinates: {info['latitude']}, {info['longitude']}")
            
            if info['city']:
                entry['city'] = info['city']
            
            if info['country']:
                entry['country'] = info['country']
            
            if info['latitude'] and info['longitude']:
                entry['coordinates'] = {
                    'lat': str(info['latitude']),
                    'lon': str(info['longitude'])
                }
        else:
            print("  Failed to fetch from PeeringDB")
    
    # Add to mapping
    mapping[code] = entry
    
    # Save
    with open(mapping_file, 'w') as f:
        json.dump(mapping, f, indent=2, sort_keys=True)
    
    print(f"\n✓ Added {code} to mapping file")
    print(f"  PeeringDB ID: {peeringdb_id or 'None'}")
    if 'coordinates' in entry:
        print(f"  Coordinates: {entry['coordinates']['lat']}, {entry['coordinates']['lon']}")

if __name__ == '__main__':
    main()
