#!/usr/bin/env python3
import json
import requests
import time
import re

def get_facility_data_from_peeringdb(peeringdb_id, retry_count=0):
    try:
        time.sleep(1)  # Base rate limiting: 1 request per second
        url = f"https://www.peeringdb.com/api/fac/{peeringdb_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                fac = data['data'][0]
                return {
                    'name': fac.get('name'),
                    'city': fac.get('city'),
                    'state': fac.get('state'),
                    'country': fac.get('country'),
                    'latitude': fac.get('latitude'),
                    'longitude': fac.get('longitude')
                }
        elif response.status_code == 429:
            # Exponential backoff: 2^retry_count seconds, max 60s
            wait_time = min(2 ** retry_count, 60)
            retry_after = response.headers.get('Retry-After')
            if retry_after:
                wait_time = int(retry_after)
            print(f"  Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
            return get_facility_data_from_peeringdb(peeringdb_id, retry_count + 1)
    except Exception as e:
        print(f"  Error: {e}")
    return None

def get_us_state_from_city(city_name, city_to_state_map):
    """Extract US state from city name using mapping - NOT USED, kept for reference"""
    for city, state in city_to_state_map.items():
        if city in city_name:
            return state
    return None

def extract_city_from_name(name):
    """Extract city name from location name - NOT USED, kept for reference"""
    parts = [p.strip() for p in name.split(',')]
    if len(parts) >= 2:
        return parts[1]
    return name

def main():
    with open('data-structures/location-mapping.json', 'r') as f:
        mapping = json.load(f)
    
    total = len([e for e in mapping.values() if e.get('peeringdb_id')])
    updated_city = 0
    updated_country = 0
    updated_coords = 0
    updated_state = 0
    processed = 0
    
    print(f"Processing {total} locations with PeeringDB IDs...\n")
    
    # Fetch data from PeeringDB and update city, country, coordinates, and state
    for code, entry in mapping.items():
        if not entry.get('peeringdb_id'):
            continue
        
        processed += 1
        print(f"[{processed}/{total}] Fetching data for {code} (PeeringDB {entry['peeringdb_id']})...")
        data = get_facility_data_from_peeringdb(entry['peeringdb_id'])
        
        if data:
            # Update city
            if data.get('city') and data['city'] != entry.get('city'):
                entry['city'] = data['city']
                print(f"  → City: {data['city']}")
                updated_city += 1
            
            # Update country
            if data['country'] and data['country'] != entry.get('country'):
                entry['country'] = data['country']
                print(f"  → Country: {data['country']}")
                updated_country += 1
            
            # Update coordinates
            if data['latitude'] and data['longitude']:
                if 'coordinates' not in entry or \
                   entry['coordinates'].get('lat') != str(data['latitude']) or \
                   entry['coordinates'].get('lon') != str(data['longitude']):
                    entry['coordinates'] = {
                        'lat': str(data['latitude']),
                        'lon': str(data['longitude'])
                    }
                    print(f"  → Coordinates: {data['latitude']}, {data['longitude']}")
                    updated_coords += 1
            
            # Update state for US locations
            if data['country'] == 'US' and data.get('state') and data['state'] != entry.get('state'):
                entry['state'] = data['state']
                print(f"  → State: {data['state']}")
                updated_state += 1
    
    if updated_city > 0 or updated_country > 0 or updated_coords > 0 or updated_state > 0:
        with open('data-structures/location-mapping.json', 'w') as f:
            json.dump(mapping, f, indent=2, sort_keys=True)
        print(f"\n✓ Updated {updated_city} entries with city data")
        print(f"✓ Updated {updated_country} entries with country data")
        print(f"✓ Updated {updated_coords} entries with coordinates")
        print(f"✓ Updated {updated_state} entries with US state data")
        print(f"\nSaved to data-structures/location-mapping.json")
    else:
        print("\nNo updates needed")

if __name__ == '__main__':
    main()
