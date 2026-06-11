#!/usr/bin/env python3
import json
import requests
import time

def api_get(url, retry_count=0):
    """Make a rate-limited GET request to PeeringDB API with retry on 429."""
    try:
        time.sleep(1)  # Base rate limiting: 1 request per second
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            wait_time = min(2 ** retry_count, 60)
            retry_after = response.headers.get('Retry-After')
            if retry_after:
                wait_time = int(retry_after)
            print(f"  Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)
            return api_get(url, retry_count + 1)
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
    return None

def get_facility_data_from_peeringdb(peeringdb_id):
    """Fetch facility data including campus info from PeeringDB."""
    data = api_get(f"https://www.peeringdb.com/api/fac/{peeringdb_id}")
    if data and 'data' in data and len(data['data']) > 0:
        fac = data['data'][0]
        result = {
            'facility_name': fac.get('name'),
            'name': fac.get('name'),
            'city': fac.get('city'),
            'state': fac.get('state'),
            'country': fac.get('country'),
            'latitude': fac.get('latitude'),
            'longitude': fac.get('longitude'),
            'org_id': fac.get('org_id'),
            'org_name': fac.get('org_name'),
            'campus_id': fac.get('campus_id'),
        }
        # Extract campus name from inline data
        campus = fac.get('campus')
        if campus:
            result['campus_name'] = campus.get('name')
            fac_set = campus.get('fac_set', [])
            if fac_set and isinstance(fac_set[0], dict):
                result['campus_facilities'] = [f.get('name', '') for f in fac_set]
            elif fac_set and isinstance(fac_set[0], int):
                result['campus_facility_ids'] = fac_set
        return result
    return None


def resolve_campus_facilities(campus_ids):
    """Resolve campus facility names in bulk using /api/campus endpoint.
    
    Takes a set of campus IDs and returns a dict mapping campus_id -> list of facility names.
    """
    campus_facilities = {}
    if not campus_ids:
        return campus_facilities
    
    id_list = list(campus_ids)
    batch_size = 20
    print(f"\n  Resolving facility names for {len(id_list)} campuses...")
    
    for i in range(0, len(id_list), batch_size):
        batch = id_list[i:i+batch_size]
        ids_param = ','.join(str(cid) for cid in batch)
        data = api_get(f"https://www.peeringdb.com/api/campus?id__in={ids_param}&depth=1")
        if data and 'data' in data:
            for campus in data['data']:
                cid = campus['id']
                fac_set = campus.get('fac_set', [])
                if fac_set and isinstance(fac_set[0], dict):
                    campus_facilities[cid] = [f.get('name', '') for f in fac_set]
                elif fac_set and isinstance(fac_set[0], int):
                    # Still just IDs, resolve via fac endpoint
                    fac_ids_param = ','.join(str(fid) for fid in fac_set)
                    fac_data = api_get(f"https://www.peeringdb.com/api/fac?id__in={fac_ids_param}")
                    if fac_data and 'data' in fac_data:
                        campus_facilities[cid] = [f.get('name', '') for f in fac_data['data']]
                    else:
                        campus_facilities[cid] = []
                else:
                    campus_facilities[cid] = []
    
    return campus_facilities

def get_carriers_for_facilities(peeringdb_ids):
    """Fetch carriers for all facilities using bulk API calls to minimize requests.
    
    Strategy: Use /api/carrierfac?fac_id__in=... to batch multiple facilities,
    then resolve carrier names with /api/carrier?id__in=...
    """
    carriers_by_fac = {}
    
    # Batch facility IDs into groups of 20 to keep URL length reasonable
    id_list = list(peeringdb_ids)
    batch_size = 20
    all_carrier_fac_entries = []
    
    print(f"\nFetching carrier data for {len(id_list)} facilities...")
    
    for i in range(0, len(id_list), batch_size):
        batch = id_list[i:i+batch_size]
        ids_param = ','.join(str(fid) for fid in batch)
        batch_num = i // batch_size + 1
        total_batches = (len(id_list) + batch_size - 1) // batch_size
        print(f"  Batch {batch_num}/{total_batches}: fetching carrierfac for {len(batch)} facilities...")
        
        data = api_get(f"https://www.peeringdb.com/api/carrierfac?fac_id__in={ids_param}")
        if data and 'data' in data:
            all_carrier_fac_entries.extend(data['data'])
    
    # Group carrier IDs by facility
    carrier_ids_by_fac = {}
    all_carrier_ids = set()
    for entry in all_carrier_fac_entries:
        fac_id = entry.get('fac_id')
        carrier_id = entry.get('carrier_id')
        if fac_id and carrier_id:
            carrier_ids_by_fac.setdefault(str(fac_id), set()).add(carrier_id)
            all_carrier_ids.add(carrier_id)
    
    # Resolve carrier names in bulk
    carrier_names = {}
    if all_carrier_ids:
        carrier_id_list = list(all_carrier_ids)
        print(f"  Resolving {len(carrier_id_list)} unique carrier names...")
        for i in range(0, len(carrier_id_list), batch_size):
            batch = carrier_id_list[i:i+batch_size]
            ids_param = ','.join(str(cid) for cid in batch)
            data = api_get(f"https://www.peeringdb.com/api/carrier?id__in={ids_param}")
            if data and 'data' in data:
                for carrier in data['data']:
                    carrier_names[carrier['id']] = carrier.get('name', f"Carrier {carrier['id']}")
    
    # Build final mapping: fac_id -> sorted list of carrier names
    for fac_id, cids in carrier_ids_by_fac.items():
        carriers_by_fac[fac_id] = sorted([carrier_names.get(cid, f"Carrier {cid}") for cid in cids])
    
    print(f"  Found carriers for {len(carriers_by_fac)} facilities")
    return carriers_by_fac

def main():
    with open('data-structures/location-mapping.json', 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    entries_with_peeringdb = {code: entry for code, entry in mapping.items() if entry.get('peeringdb_id')}
    total = len(entries_with_peeringdb)
    updated_facility_name = 0
    updated_city = 0
    updated_country = 0
    updated_coords = 0
    updated_state = 0
    updated_org = 0
    updated_campus = 0
    updated_carriers = 0
    processed = 0
    
    print(f"Processing {total} locations with PeeringDB IDs...\n")
    
    # Phase 1: Fetch facility data (includes campus info inline)
    print("=== Phase 1: Fetching facility data ===\n")
    for code, entry in mapping.items():
        if not entry.get('peeringdb_id'):
            continue
        
        processed += 1
        print(f"[{processed}/{total}] Fetching data for {code} (PeeringDB {entry['peeringdb_id']})...")
        data = get_facility_data_from_peeringdb(entry['peeringdb_id'])
        
        if data:
            # Update facility name
            if data.get('facility_name') and data['facility_name'] != entry.get('facility_name'):
                entry['facility_name'] = data['facility_name']
                print(f"  → Facility: {data['facility_name']}")
                updated_facility_name += 1
            
            # Update city
            if data.get('city') and data['city'] != entry.get('city'):
                entry['city'] = data['city']
                print(f"  → City: {data['city']}")
                updated_city += 1
            
            # Update country
            if data.get('country') and data['country'] != entry.get('country'):
                entry['country'] = data['country']
                print(f"  → Country: {data['country']}")
                updated_country += 1
            
            # Update coordinates
            if data.get('latitude') and data.get('longitude'):
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
            if data.get('country') == 'US' and data.get('state') and data['state'] != entry.get('state'):
                entry['state'] = data['state']
                print(f"  → State: {data['state']}")
                updated_state += 1
            
            # Update organization data
            if data.get('org_id') and data['org_id'] != entry.get('org_id'):
                entry['org_id'] = data['org_id']
                updated_org += 1
            if data.get('org_name') and data['org_name'] != entry.get('org_name'):
                entry['org_name'] = data['org_name']
                print(f"  → Organization: {data['org_name']}")
                updated_org += 1
            
            # Update campus data
            if data.get('campus_name'):
                new_campus = {
                    'name': data['campus_name'],
                    'facilities': data.get('campus_facilities', [])
                }
                # Store campus_id for bulk resolution if facilities are just IDs
                if not new_campus['facilities'] and data.get('campus_facility_ids'):
                    new_campus['_campus_id'] = data.get('campus_id')
                    new_campus['_facility_ids'] = data.get('campus_facility_ids')
                if entry.get('campus', {}).get('name') != new_campus['name']:
                    entry['campus'] = new_campus
                    print(f"  → Campus: {data['campus_name']}")
                    updated_campus += 1
            elif 'campus' in entry and not data.get('campus_id'):
                # Campus was removed
                del entry['campus']
                updated_campus += 1
    
    # Phase 1b: Resolve campus facility names in bulk
    print("\n=== Phase 1b: Resolving campus facility names ===")
    campus_ids_to_resolve = set()
    for code, entry in mapping.items():
        campus = entry.get('campus', {})
        if campus.get('_campus_id') and not campus.get('facilities'):
            campus_ids_to_resolve.add(campus['_campus_id'])
    
    if campus_ids_to_resolve:
        resolved = resolve_campus_facilities(campus_ids_to_resolve)
        for code, entry in mapping.items():
            campus = entry.get('campus', {})
            if campus.get('_campus_id') in resolved:
                entry['campus'] = {
                    'name': campus['name'],
                    'facilities': resolved[campus['_campus_id']]
                }
                updated_campus += 1
        print(f"  Resolved {len(resolved)} campuses")
    else:
        print("  No campuses to resolve")
    
    # Phase 2: Fetch carrier data in bulk (minimizes API calls)
    print("\n=== Phase 2: Fetching carrier data (bulk) ===")
    peeringdb_ids = [int(entry['peeringdb_id']) for entry in entries_with_peeringdb.values()]
    carriers_by_fac = get_carriers_for_facilities(peeringdb_ids)
    
    # Apply carrier data to mapping
    for code, entry in mapping.items():
        if not entry.get('peeringdb_id'):
            continue
        fac_id = str(entry['peeringdb_id'])
        new_carriers = carriers_by_fac.get(fac_id, [])
        if entry.get('carriers') != new_carriers:
            if new_carriers:
                entry['carriers'] = new_carriers
            elif 'carriers' in entry:
                del entry['carriers']
            updated_carriers += 1
    
    # Save results
    any_updates = (updated_facility_name + updated_city + updated_country + 
                   updated_coords + updated_state + updated_org + 
                   updated_campus + updated_carriers) > 0
    
    if any_updates:
        with open('data-structures/location-mapping.json', 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, sort_keys=True)
        print(f"\n{'='*50}")
        print(f"✓ Updated {updated_facility_name} entries with facility name")
        print(f"✓ Updated {updated_city} entries with city data")
        print(f"✓ Updated {updated_country} entries with country data")
        print(f"✓ Updated {updated_coords} entries with coordinates")
        print(f"✓ Updated {updated_state} entries with US state data")
        print(f"✓ Updated {updated_org} entries with organization data")
        print(f"✓ Updated {updated_campus} entries with campus data")
        print(f"✓ Updated {updated_carriers} entries with carrier data")
        print(f"\nSaved to data-structures/location-mapping.json")
    else:
        print("\nNo updates needed")

if __name__ == '__main__':
    main()
