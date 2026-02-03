#!/usr/bin/env python3
import json
from datetime import datetime

# Read the data (use merged if available)
try:
    with open('data-structures/dx-locations-data-merged.json', 'r') as f:
        locations = json.load(f)
except FileNotFoundError:
    with open('data-structures/dx-locations-data.json', 'r') as f:
        locations = json.load(f)

# Read the icon
with open('icons/icon.txt', 'r') as f:
    icon_data = f.read().strip()

# Read region mapping
with open('data-structures/region-mapping.json', 'r') as f:
    region_mapping = json.load(f)

# Read country mapping (reverse it for code -> name)
with open('data-structures/country-mapping.json', 'r') as f:
    country_mapping_raw = json.load(f)
    country_code_to_name = {v: k for k, v in country_mapping_raw.items() if len(k) > 2}

# Sort by name (location name), handling None values
sorted_locations = sorted(locations, key=lambda x: x['name'] or x.get('aws_name', ''))

# Generate HTML
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS Direct Connect Locations</title>
    <link rel="icon" type="image/jpeg" href="{icon_data}">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"/>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #232f3e; display: flex; align-items: center; gap: 10px; }}
        h1 img {{ height: 40px; width: 40px; }}
        #map {{ height: 500px; width: 100%; margin-bottom: 20px; border: 2px solid #ddd; border-radius: 4px; background: white; position: relative; }}
        .home-button {{ position: absolute; bottom: 10px; left: 10px; z-index: 1000; background: white; border: 2px solid #ccc; border-radius: 4px; padding: 8px 12px; cursor: pointer; font-size: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        .home-button:hover {{ background: #f0f0f0; }}
        .tabs {{ display: flex; margin-bottom: 20px; border-bottom: 2px solid #ddd; }}
        .tab {{ padding: 12px 24px; cursor: pointer; border: none; background: none; font-size: 16px; color: #666; border-bottom: 3px solid transparent; transition: all 0.3s ease; }}
        .tab:hover {{ color: #232f3e; background: #f5f5f5; }}
        .tab.active {{ color: #232f3e; border-bottom-color: #0073bb; background: white; font-weight: 600; }}
        .partition-info {{ display: inline-flex; align-items: center; gap: 8px; margin-left: 8px; }}
        .filters {{ display: flex; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; align-items: flex-start; }}
        .filters select {{ padding: 8px 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 14px; background: white; cursor: pointer; }}
        .filters select:hover {{ border-color: #999; }}
        .multi-select {{ position: relative; min-width: 200px; }}
        .multi-select-trigger {{ padding: 8px 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 14px; background: white; cursor: pointer; display: flex; justify-content: space-between; align-items: center; gap: 8px; }}
        .multi-select-trigger:hover {{ border-color: #999; }}
        .multi-select-trigger.active {{ border-color: #0073bb; }}
        .multi-select-dropdown {{ position: absolute; top: 100%; left: 0; min-width: 250px; background: white; border: 2px solid #ddd; border-radius: 4px; margin-top: 4px; max-height: 300px; overflow-y: auto; display: none; z-index: 1000; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .multi-select-dropdown.show {{ display: block; }}
        .multi-select-actions {{ display: flex; gap: 8px; padding: 8px; border-bottom: 1px solid #ddd; background: #f9f9f9; }}
        .multi-select-actions button {{ padding: 4px 12px; border: 1px solid #ddd; border-radius: 3px; background: white; cursor: pointer; font-size: 12px; flex: 1; }}
        .multi-select-actions button:hover {{ background: #e8e8e8; }}
        .multi-select-option {{ padding: 8px 12px; cursor: pointer; display: flex; align-items: center; gap: 8px; }}
        .multi-select-option:hover {{ background: #f0f0f0; }}
        .multi-select-option input[type="checkbox"] {{ cursor: pointer; }}
        .country-tags {{ display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }}
        .country-tag {{ display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; background: #0073bb; color: white; border-radius: 16px; font-size: 13px; }}
        .country-tag button {{ background: none; border: none; color: white; cursor: pointer; font-size: 16px; padding: 0; margin: 0; line-height: 1; }}
        .country-tag button:hover {{ color: #ffcccc; }}
        .reset-filters {{ padding: 8px 16px; border: 2px solid #ddd; border-radius: 4px; font-size: 14px; background: white; cursor: pointer; display: none; }}
        .reset-filters:hover {{ background: #f0f0f0; border-color: #999; }}
        .location-count {{ padding: 8px 12px; font-size: 14px; color: #666; }}
        .search-container {{ position: relative; margin-bottom: 15px; }}
        #searchInput {{ width: 100%; padding: 12px 40px 12px 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 16px; box-sizing: border-box; }}
        .clear-btn {{ position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; font-size: 20px; cursor: pointer; color: #999; display: none; }}
        .clear-btn:hover {{ color: #333; }}
        table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th {{ background: #232f3e; color: white; padding: 12px; text-align: left; cursor: pointer; user-select: none; position: relative; }}
        th:hover {{ background: #37475a; }}
        th.no-sort {{ cursor: default; }}
        th.no-sort:hover {{ background: #232f3e; }}
        th.asc::after {{ content: ' ▲'; position: absolute; right: 10px; }}
        th.desc::after {{ content: ' ▼'; position: absolute; right: 10px; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tbody tr {{ cursor: pointer; }}
        tr:hover {{ background: #f9f9f9; }}
        a {{ color: #0073bb; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .info-icon {{ display: inline-block; width: 16px; height: 16px; line-height: 16px; text-align: center; background: #0073bb; color: white; border-radius: 50%; font-size: 12px; font-weight: bold; margin-left: 5px; cursor: help; position: relative; }}
        .info-icon:hover::after {{ content: attr(data-tooltip); position: absolute; bottom: 125%; right: 0; background: #333; color: white; padding: 8px 12px; border-radius: 4px; white-space: normal; width: 300px; font-size: 13px; font-weight: normal; z-index: 1000; line-height: 1.4; }}
        .info-icon:hover::before {{ content: ''; position: absolute; bottom: 115%; right: 10px; border: 6px solid transparent; border-top-color: #333; }}
        .warning-icon {{ display: inline-block; margin-left: 5px; cursor: help; position: relative; vertical-align: text-top; }}
        .warning-icon svg {{ width: 24px; height: 24px; color: #ff9800; display: block; }}
        .warning-icon:hover::after {{ content: attr(data-tooltip); position: absolute; bottom: 125%; right: 0; background: #333; color: white; padding: 8px 12px; border-radius: 4px; white-space: normal; width: 300px; font-size: 13px; font-weight: normal; z-index: 1000; line-height: 1.4; pointer-events: none; }}
        .warning-icon:hover::before {{ content: ''; position: absolute; bottom: 115%; right: 10px; border: 6px solid transparent; border-top-color: #333; pointer-events: none; }}
        .footer {{ margin-top: 30px; padding: 20px; text-align: center; color: #666; font-size: 14px; border-top: 1px solid #ddd; background: white; }}
        .footer a {{ color: #0073bb; text-decoration: none; }}
        .footer a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1><img src="{icon_data}" alt="AWS Direct Connect">AWS Direct Connect Locations</h1>
    <div id="map">
        <button class="home-button" onclick="resetMap(); event.stopPropagation();" title="Reset map view">🏠</button>
    </div>
    <div class="tabs">
        <button class="tab active" onclick="switchPartition('aws')" id="tab-aws">
            <svg width="1em" height="1em" viewBox="0 0 25 25" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-right: 8px;"><path d="M5.5 16.5H19.5M5.5 8.5H19.5M4.5 12.5H20.5M12.5 20.5C12.5 20.5 8 18.5 8 12.5C8 6.5 12.5 4.5 12.5 4.5M12.5 4.5C12.5 4.5 17 6.5 17 12.5C17 18.5 12.5 20.5 12.5 20.5M12.5 4.5V20.5M20.5 12.5C20.5 16.9183 16.9183 20.5 12.5 20.5C8.08172 20.5 4.5 16.9183 4.5 12.5C4.5 8.08172 8.08172 4.5 12.5 4.5C16.9183 4.5 20.5 8.08172 20.5 12.5Z" stroke="currentColor" stroke-width="1.2"/></svg>
            AWS Commercial
        </button>
        <button class="tab" onclick="switchPartition('aws-govcloud')" id="tab-aws-govcloud">
            <img src="GovCloud.png" style="height: 1em; width: 2em; margin-right: 8px; object-fit: contain;" alt="GovCloud">
            AWS GovCloud (US)
            <div class="partition-info">
                <span class="info-icon" data-tooltip="Direct Connect Gateway enables connectivity from any Direct Connect location to AWS GovCloud (US) regions. Cross-account connectivity is supported between GovCloud and commercial accounts." onclick="event.stopPropagation()">i</span>
            </div>
        </button>
        <button class="tab" onclick="switchPartition('aws-eusc')" id="tab-aws-eusc">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 810 540" style="height: 1em; width: 1.5em; margin-right: 8px;"><rect fill="#039" width="810" height="540"/><g fill="#fc0" transform="scale(30)translate(13.5,9)"><use href="#s" y="-6"/><use href="#s" y="6"/><g id="l"><use href="#s" x="-6"/><use href="#s" transform="rotate(150)translate(0,6)rotate(66)"/><use href="#s" transform="rotate(120)translate(0,6)rotate(24)"/><use href="#s" transform="rotate(60)translate(0,6)rotate(12)"/><use href="#s" transform="rotate(30)translate(0,6)rotate(42)"/></g><use href="#l" transform="scale(-1,1)"/></g><defs><g id="s"><g id="c"><path id="t" d="M0,0v1h0.5z" transform="translate(0,-1)rotate(18)"/><use href="#t" transform="scale(-1,1)"/></g><g id="a"><use href="#c" transform="rotate(72)"/><use href="#c" transform="rotate(144)"/></g><use href="#a" transform="scale(-1,1)"/></g></defs></svg>
            EU Sovereign Cloud
            <div class="partition-info">
                <span class="info-icon" data-tooltip="EU Sovereign Cloud is an isolated AWS partition designed to meet strict European data residency and sovereignty requirements. It operates independently from other AWS partitions." onclick="event.stopPropagation()">i</span>
            </div>
        </button>
        <button class="tab" onclick="switchPartition('aws-cn')" id="tab-aws-cn">
            <img src="cn.svg" style="height: 1em; width: 1.5em; margin-right: 8px; object-fit: contain;" alt="China">
            AWS China
            <div class="partition-info">
                <span class="info-icon" data-tooltip="AWS China is an isolated AWS partition operated by local partners (Sinnet in Beijing, NWCD in Ningxia) to meet Chinese regulatory requirements. It operates independently from other AWS partitions." onclick="event.stopPropagation()">i</span>
            </div>
        </button>
    </div>
    <div class="filters">
        <div class="multi-select" id="countryMultiSelect">
            <div class="multi-select-trigger" onclick="toggleCountryDropdown()">
                <span>Country Filter</span>
                <span>▼</span>
            </div>
            <div class="multi-select-dropdown" id="countryDropdown">
                <div class="multi-select-actions">
                    <button onclick="selectAllCountries(); event.stopPropagation();">Select All</button>
                    <button onclick="clearAllCountries(); event.stopPropagation();">Clear All</button>
                </div>
            </div>
        </div>
        <div class="country-tags" id="countryTags"></div>
        <select id="orgFilter" onchange="filterTable()">
            <option value="">All Organizations</option>
        </select>
        <select id="speedFilter" onchange="filterTable()">
            <option value="">All Port Speeds</option>
        </select>
        <select id="macsecFilter" onchange="filterTable()">
            <option value="">All (MACsec & Non-MACsec)</option>
            <option value="macsec">With MACsec</option>
            <option value="no-macsec">Without MACsec</option>
        </select>
        <select id="regionFilter" onchange="filterTable()">
            <option value="">All Associated Regions</option>
        </select>
        <button class="reset-filters" id="resetFilters" onclick="resetFilters()">Reset Filters</button>
        <span class="location-count" id="locationCount"></span>
    </div>
    <div class="search-container">
        <input type="text" id="searchInput" placeholder="Search locations..." onkeyup="filterTable()" oninput="toggleClearBtn()">
        <button class="clear-btn" id="clearBtn" onclick="clearSearch()">✕</button>
    </div>
    <table id="dxTable">
        <thead>
            <tr>
                <th onclick="sortTable(0)" id="th0">Location</th>
                <th onclick="sortTable(1)" id="th1">Organization</th>
                <th class="no-sort" id="th2" style="text-align: center;">Google Maps</th>
                <th onclick="sortTable(3)" id="th3">AWS Code</th>
                <th onclick="sortTable(4)" id="th4">Port Speeds</th>
                <th onclick="sortTable(5)" id="th5">Associated Region<span class="info-icon" data-tooltip="The AWS region used for API calls to manage Direct Connect resources at this location. Virtual interfaces created at this location can connect to any AWS region globally. Note: Opt-in regions must be enabled in your AWS account before locations in those regions become selectable." onclick="event.stopPropagation()">i</span></th>
            </tr>
        </thead>
        <tbody>
"""

# Add table rows with data attributes
for loc in sorted_locations:
    # Build location display with PeeringDB name and AWS name
    location_html = ""
    display_name = loc['name'] or loc.get('aws_name', 'Unknown')
    if loc.get('peeringdb_id'):
        location_html = f"<a href='https://www.peeringdb.com/fac/{loc['peeringdb_id']}' target='_blank'>{display_name}</a>"
    else:
        location_html = display_name
    
    # Add AWS name below if different from main name
    if loc.get('aws_name') and loc['aws_name'] != display_name:
        location_html += f"<br><code>AWS Name: {loc['aws_name']}</code>"
    
    # Build organization display with PeeringDB link
    org_html = ""
    if loc.get('org_id') and loc.get('org_name'):
        org_html = f"<a href='https://www.peeringdb.com/org/{loc['org_id']}' target='_blank'>{loc['org_name']}</a>"
    
    # Get partition early for use in map icon
    partition = loc.get('partition', 'aws')
    
    # Map icon in separate column with warning for China locations
    map_html = ""
    if loc.get('latitude') and loc.get('longitude'):
        if partition == 'aws-cn':
            # China locations: only show warning icon
            map_html = '<span class="warning-icon" data-tooltip="Due to the lack of PeeringDB data for AWS Direct Connect colocation facilities in China, all locations are only approximate."><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="#ffa500" style="vertical-align: middle;"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M12 1.67c.955 0 1.845 .467 2.39 1.247l.105 .16l8.114 13.548a2.914 2.914 0 0 1 -2.307 4.363l-.195 .008h-16.225a2.914 2.914 0 0 1 -2.582 -4.2l.099 -.185l8.11 -13.538a2.914 2.914 0 0 1 2.491 -1.403zm.01 13.33l-.127 .007a1 1 0 0 0 0 1.986l.117 .007l.127 -.007a1 1 0 0 0 0 -1.986l-.117 -.007zm-.01 -7a1 1 0 0 0 -.993 .883l-.007 .117v4l.007 .117a1 1 0 0 0 1.986 0l.007 -.117v-4l-.007 -.117a1 1 0 0 0 -.993 -.883z" /></svg></span>'
        else:
            # Other partitions: show Google Maps link
            map_html = f"<a href='https://maps.google.com/?q={loc['latitude']},{loc['longitude']}' target='_blank' title='View on Google Maps'><svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align: middle;'><path stroke='none' d='M0 0h24v24H0z' fill='none'/><path d='M12 18.5l-3 -1.5l-6 3v-13l6 -3l6 3l6 -3v7.5' /><path d='M9 4v13' /><path d='M15 7v5.5' /><path d='M21.121 20.121a3 3 0 1 0 -4.242 0c.418 .419 1.125 1.045 2.121 1.879c1.051 -.89 1.759 -1.516 2.121 -1.879' /><path d='M19 18v.01' /></svg></a>"
    
    speeds_unlocked = ', '.join(loc.get('port_speeds', []))
    speeds_macsec = ', '.join(loc.get('macsec_capable', []))
    speeds_html = f"<span title='Without MACsec'><svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align: middle;'><path stroke='none' d='M0 0h24v24H0z' fill='none'/><path d='M3 13a2 2 0 0 1 2 -2h10a2 2 0 0 1 2 2v6a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2l0 -6' /><path d='M9 16a1 1 0 1 0 2 0a1 1 0 0 0 -2 0' /><path d='M13 11v-4a4 4 0 1 1 8 0v4' /></svg></span> {speeds_unlocked}" if speeds_unlocked else ""
    if speeds_macsec:
        speeds_html += f"<br><span title='With MACsec'><svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='currentColor' style='vertical-align: middle;'><path stroke='none' d='M0 0h24v24H0z' fill='none'/><path d='M12 2a5 5 0 0 1 5 5v3a3 3 0 0 1 3 3v6a3 3 0 0 1 -3 3h-10a3 3 0 0 1 -3 -3v-6a3 3 0 0 1 3 -3v-3a5 5 0 0 1 5 -5m0 12a2 2 0 0 0 -1.995 1.85l-.005 .15a2 2 0 1 0 2 -2m0 -10a3 3 0 0 0 -3 3v3h6v-3a3 3 0 0 0 -3 -3' /></svg></span> {speeds_macsec}"
    
    map_link = loc['code']
    
    region_name = region_mapping.get('aws_region_names', {}).get(loc['region'], loc['region'])
    region_opt_status = loc.get('region_opt_status', 'ENABLED_BY_DEFAULT')
    opt_in_warning = ''
    if region_opt_status == 'ENABLED':
        opt_in_warning = '<span class="warning-icon" data-tooltip="This Direct Connect location is associated with an opt-in region. To use this location in the AWS Console or API, you must first enable this region in your AWS account."><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path stroke="none" d="M0 0h24v24H0z" fill="none"/><path d="M12 1.67c.955 0 1.845 .467 2.39 1.247l.105 .16l8.114 13.548a2.914 2.914 0 0 1 -2.307 4.363l-.195 .008h-16.225a2.914 2.914 0 0 1 -2.582 -4.2l.099 -.185l8.11 -13.538a2.914 2.914 0 0 1 2.491 -1.403zm.01 13.33l-.127 .007a1 1 0 0 0 0 1.986l.117 .007l.127 -.007a1 1 0 0 0 0 -1.986l-.117 -.007zm-.01 -7a1 1 0 0 0 -.993 .883l-.007 .117v4l.007 .117a1 1 0 0 0 1.986 0l.007 -.117v-4l-.007 -.117a1 1 0 0 0 -.993 -.883z" /></svg></span>'
    region_html = f"{region_name}{opt_in_warning}<br><code>{loc['region']}</code>"
    
    # Data attributes for filtering
    country_code = loc.get('country', '')
    country_name = country_code_to_name.get(country_code, country_code)
    country_display = f"{country_name} ({country_code})" if country_code and country_name else ""
    region = loc['region']
    port_speeds = ','.join(loc.get('port_speeds', []))
    macsec_speeds = ','.join(loc.get('macsec_capable', []))
    org_name = loc.get('org_name', '')
    
    html += f"""            <tr data-code="{loc['code']}" data-partition="{partition}" data-country="{country_display}" data-region="{region}" data-org="{org_name}" data-speeds="{port_speeds}" data-macsec="{macsec_speeds}">
                <td>{location_html}</td>
                <td>{org_html}</td>
                <td style="text-align: center;">{map_html}</td>
                <td>{map_link}</td>
                <td>{speeds_html}</td>
                <td>{region_html}</td>
            </tr>
"""

html += """        </tbody>
    </table>
    <script>
        // Map setup
        const map = L.map('map').setView([20, 0], 2);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
        
        // Icon
        const customIcon = L.icon({
            iconUrl: '""" + icon_data + """',
            iconSize: [24, 24]
        });
        
        // Markers storage
        const markers = {};
        const labels = {};
        let selectedCode = null;
        let userMarker = null;
        let nearestLines = [];
        const locationsData = """ + json.dumps([{"code": loc['code'], "lat": loc.get('latitude'), "lon": loc.get('longitude')} for loc in locations if loc.get('latitude') and loc.get('longitude')]) + """;
        
        // Haversine distance calculation
        function getDistance(lat1, lon1, lat2, lon2) {
            const R = 6371; // Earth radius in km
            const dLat = (lat2 - lat1) * Math.PI / 180;
            const dLon = (lon2 - lon1) * Math.PI / 180;
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                      Math.sin(dLon/2) * Math.sin(dLon/2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            return R * c;
        }
        
        // Find nearest locations from currently visible ones
        function findNearest(lat, lon) {
            // Get currently visible location codes from table
            const visibleCodes = new Set();
            const table = document.getElementById('dxTable');
            const tr = table.getElementsByTagName('tr');
            for (let i = 1; i < tr.length; i++) {
                if (tr[i].style.display !== 'none') {
                    visibleCodes.add(tr[i].getAttribute('data-code'));
                }
            }
            
            const distances = locationsData
                .filter(loc => visibleCodes.has(loc.code))
                .map(loc => ({
                    code: loc.code,
                    lat: loc.lat,
                    lon: loc.lon,
                    distance: getDistance(lat, lon, loc.lat, loc.lon)
                }))
                .sort((a, b) => a.distance - b.distance);
            return distances.slice(0, 2);
        }
        
        // Place user marker
        map.on('click', function(e) {
            if (userMarker) {
                map.removeLayer(userMarker);
                nearestLines.forEach(line => map.removeLayer(line));
                nearestLines = [];
                document.getElementById('searchInput').value = '';
                toggleClearBtn();
                filterTable();
                userMarker = null;
                return;
            }
            
            const userIcon = L.icon({
                iconUrl: 'data:image/svg+xml;base64,' + btoa('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#e74c3c" stroke="white" stroke-width="2"><circle cx="12" cy="12" r="8"/></svg>'),
                iconSize: [24, 24]
            });
            
            userMarker = L.marker([e.latlng.lat, e.latlng.lng], {icon: userIcon})
                .addTo(map)
                .on('click', function(ev) {
                    L.DomEvent.stopPropagation(ev);
                    map.removeLayer(userMarker);
                    nearestLines.forEach(line => map.removeLayer(line));
                    nearestLines = [];
                    userMarker = null;
                    document.getElementById('searchInput').value = '';
                    toggleClearBtn();
                    filterTable();
                });
            
            const nearest = findNearest(e.latlng.lat, e.latlng.lng);
            
            nearest.forEach(loc => {
                const line = L.polyline([[e.latlng.lat, e.latlng.lng], [loc.lat, loc.lon]], {
                    color: '#0073bb',
                    weight: 2,
                    opacity: 0.7
                }).addTo(map);
                nearestLines.push(line);
            });
            
            const codes = nearest.map(loc => loc.code).join('|');
            document.getElementById('searchInput').value = codes;
            toggleClearBtn();
            
            // Show only nearest locations
            const nearestCodes = new Set(nearest.map(loc => loc.code));
            const table = document.getElementById("dxTable");
            const tr = table.getElementsByTagName("tr");
            for (let i = 1; i < tr.length; i++) {
                const code = tr[i].getAttribute('data-code');
                tr[i].style.display = nearestCodes.has(code) ? "" : "none";
            }
            
            // Show only nearest markers
            Object.keys(markers).forEach(code => {
                if (nearestCodes.has(code)) {
                    map.addLayer(markers[code]);
                    map.addLayer(labels[code]);
                } else {
                    map.removeLayer(markers[code]);
                    map.removeLayer(labels[code]);
                }
            });
        });
        
        // Populate filter dropdowns
        const countries = new Set();
        const orgs = new Set();
        const regions = new Set();
        const speeds = new Set();
        const selectedCountries = new Set();
        
        // Populate dropdowns based on all data initially
        function populateFilters(partition) {
            countries.clear();
            orgs.clear();
            regions.clear();
            speeds.clear();
            
            document.querySelectorAll('tr[data-country]').forEach(tr => {
                const rowPartition = tr.dataset.partition || 'aws';
                if (rowPartition === partition) {
                    if (tr.dataset.country) countries.add(tr.dataset.country);
                    if (tr.dataset.org) orgs.add(tr.dataset.org);
                    if (tr.dataset.region) regions.add(tr.dataset.region);
                    if (tr.dataset.speeds) tr.dataset.speeds.split(',').forEach(s => speeds.add(s));
                    if (tr.dataset.macsec) tr.dataset.macsec.split(',').forEach(s => speeds.add(s));
                }
            });
            
            // Repopulate country multi-select
            const countryDropdown = document.getElementById('countryDropdown');
            const actionsDiv = countryDropdown.querySelector('.multi-select-actions');
            countryDropdown.innerHTML = '';
            countryDropdown.appendChild(actionsDiv);
            
            const sortedCountries = Array.from(countries).filter(c => c).sort((a, b) => {
                const nameA = a.split(' (')[0];
                const nameB = b.split(' (')[0];
                return nameA.localeCompare(nameB);
            });
            sortedCountries.forEach(c => {
                const option = document.createElement('div');
                option.className = 'multi-select-option';
                option.innerHTML = `<input type="checkbox" id="country-${c}" value="${c}" onchange="updateCountryFilter()"><label for="country-${c}" style="cursor: pointer; flex: 1;">${c}</label>`;
                countryDropdown.appendChild(option);
            });
            
            // Repopulate organization filter
            const orgFilter = document.getElementById('orgFilter');
            const currentOrg = orgFilter.value;
            orgFilter.innerHTML = '<option value="">All Organizations</option>';
            Array.from(orgs).filter(o => o).sort().forEach(o => {
                const opt = document.createElement('option');
                opt.value = o;
                opt.textContent = o;
                orgFilter.appendChild(opt);
            });
            if (orgs.has(currentOrg)) {
                orgFilter.value = currentOrg;
            }
            
            // Repopulate region filter
            const regionFilter = document.getElementById('regionFilter');
            const currentRegion = regionFilter.value;
            regionFilter.innerHTML = '<option value="">All Associated Regions</option>';
            Array.from(regions).sort().forEach(r => {
                const opt = document.createElement('option');
                opt.value = r;
                opt.textContent = r;
                regionFilter.appendChild(opt);
            });
            if (regions.has(currentRegion)) {
                regionFilter.value = currentRegion;
            }
            
            // Repopulate speed filter
            const speedFilter = document.getElementById('speedFilter');
            const currentSpeed = speedFilter.value;
            speedFilter.innerHTML = '<option value="">All Port Speeds</option>';
            Array.from(speeds).sort((a,b) => {
                const order = {'1G':1, '10G':2, '100G':3, '400G':4};
                return (order[a]||99) - (order[b]||99);
            }).forEach(s => {
                const opt = document.createElement('option');
                opt.value = s;
                opt.textContent = s;
                speedFilter.appendChild(opt);
            });
            if (speeds.has(currentSpeed)) {
                speedFilter.value = currentSpeed;
            }
        }
        
        document.querySelectorAll('tr[data-country]').forEach(tr => {
            if (tr.dataset.country) countries.add(tr.dataset.country);
            if (tr.dataset.org) orgs.add(tr.dataset.org);
            if (tr.dataset.region) regions.add(tr.dataset.region);
            if (tr.dataset.speeds) tr.dataset.speeds.split(',').forEach(s => speeds.add(s));
            if (tr.dataset.macsec) tr.dataset.macsec.split(',').forEach(s => speeds.add(s));
        });
        
        // Populate country multi-select (initial)
        const countryDropdown = document.getElementById('countryDropdown');
        populateFilters('aws');
        
        // Add click handlers to table rows
        document.querySelectorAll('#dxTable tbody tr').forEach(row => {
            row.addEventListener('click', function(e) {
                if (e.target.tagName === 'A') return;
                const code = this.getAttribute('data-code');
                if (code) zoomToLocation(code);
            });
        });
        
"""

# Add markers
for loc in locations:
    if loc.get('latitude') and loc.get('longitude'):
        html += f"""        markers['{loc['code']}'] = L.marker([{loc['latitude']}, {loc['longitude']}], {{icon: customIcon}})
            .on('click', function(e) {{ L.DomEvent.stopPropagation(e); selectLocation('{loc['code']}'); }})
            .addTo(map);
        labels['{loc['code']}'] = L.marker([{loc['latitude']}, {loc['longitude']}], {{
            icon: L.divIcon({{
                html: '<div style="font-size: 10px; font-weight: bold; color: #232f3e; text-shadow: 1px 1px 2px white, -1px -1px 2px white, 1px -1px 2px white, -1px 1px 2px white; white-space: nowrap; margin-top: 20px;">{loc['code']}</div>',
                className: 'empty'
            }})
        }})
            .on('click', function(e) {{ L.DomEvent.stopPropagation(e); selectLocation('{loc['code']}'); }})
            .addTo(map);
"""

html += """
        // Table sorting
        let currentSort = { col: -1, dir: 'asc' };
        
        function sortTable(n) {
            const table = document.getElementById("dxTable");
            const tbody = table.tBodies[0];
            const rows = Array.from(tbody.rows);
            
            if (currentSort.col === n) {
                currentSort.dir = currentSort.dir === 'asc' ? 'desc' : 'asc';
            } else {
                currentSort.col = n;
                currentSort.dir = 'asc';
            }
            
            rows.sort((a, b) => {
                const aText = a.cells[n].textContent.trim();
                const bText = b.cells[n].textContent.trim();
                const compare = aText.localeCompare(bText, undefined, { numeric: true });
                return currentSort.dir === 'asc' ? compare : -compare;
            });
            
            rows.forEach(row => tbody.appendChild(row));
            
            document.querySelectorAll('th').forEach(th => th.classList.remove('asc', 'desc'));
            document.getElementById('th' + n).classList.add(currentSort.dir);
        }
        
        // Select location from map
        function selectLocation(code) {
            if (userMarker) return;
            const loc = locationsData.find(l => l.code === code);
            if (loc) {
                map.setView([loc.lat, loc.lon], 12);
            }
            document.getElementById('searchInput').value = code;
            toggleClearBtn();
            filterTable();
        }
        
        // Zoom to location from table row
        function zoomToLocation(code) {
            if (userMarker) return;
            const loc = locationsData.find(l => l.code === code);
            if (loc) {
                map.setView([loc.lat, loc.lon], 12);
            }
        }
        
        // Reset map view
        function resetMap() {
            clearUserMarker();
            const currentPartition = getCurrentPartition();
            if (currentPartition === 'aws-eusc') {
                map.setView([50, 10], 4); // EU view for EUSC
            } else if (currentPartition === 'aws-cn') {
                map.setView([35, 105], 4); // China view for China
            } else {
                map.setView([20, 0], 2); // World view for AWS Commercial
            }
            document.getElementById('searchInput').value = '';
            toggleClearBtn();
            filterTable();
        }
        
        // Toggle clear button visibility
        function toggleClearBtn() {
            const input = document.getElementById('searchInput');
            const clearBtn = document.getElementById('clearBtn');
            clearBtn.style.display = input.value ? 'block' : 'none';
        }
        
        // Clear search
        function clearSearch() {
            clearUserMarker();
            selectedCode = null;
            document.getElementById('searchInput').value = '';
            clearAllCountries();
            document.getElementById('orgFilter').value = '';
            document.getElementById('regionFilter').value = '';
            document.getElementById('speedFilter').value = '';
            document.getElementById('macsecFilter').value = '';
            toggleClearBtn();
            filterTable();
        }
        
        // Clear user marker and lines
        function clearUserMarker() {
            if (userMarker) {
                map.removeLayer(userMarker);
                nearestLines.forEach(line => map.removeLayer(line));
                nearestLines = [];
                userMarker = null;
            }
        }
        
        // Reset filters
        function resetFilters() {
            clearUserMarker();
            document.getElementById('searchInput').value = '';
            toggleClearBtn();
            clearAllCountries();
            document.getElementById('orgFilter').value = '';
            document.getElementById('regionFilter').value = '';
            document.getElementById('speedFilter').value = '';
            document.getElementById('macsecFilter').value = '';
            filterTable();
        }
        
        // Toggle country dropdown
        function toggleCountryDropdown() {
            const dropdown = document.getElementById('countryDropdown');
            dropdown.classList.toggle('show');
            document.getElementById('countryMultiSelect').querySelector('.multi-select-trigger').classList.toggle('active');
        }
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!document.getElementById('countryMultiSelect').contains(e.target)) {
                document.getElementById('countryDropdown').classList.remove('show');
                document.getElementById('countryMultiSelect').querySelector('.multi-select-trigger').classList.remove('active');
            }
        });
        
        // Select all countries
        function selectAllCountries() {
            document.querySelectorAll('#countryDropdown input[type="checkbox"]').forEach(cb => cb.checked = true);
            updateCountryFilter();
        }
        
        // Clear all countries
        function clearAllCountries() {
            document.querySelectorAll('#countryDropdown input[type="checkbox"]').forEach(cb => cb.checked = false);
            updateCountryFilter();
        }
        
        // Update country filter and tags
        function updateCountryFilter() {
            selectedCountries.clear();
            document.querySelectorAll('#countryDropdown input[type="checkbox"]:checked').forEach(cb => {
                selectedCountries.add(cb.value);
            });
            
            // Update tags
            const tagsContainer = document.getElementById('countryTags');
            tagsContainer.innerHTML = '';
            Array.from(selectedCountries).sort().forEach(country => {
                const tag = document.createElement('div');
                tag.className = 'country-tag';
                tag.innerHTML = `${country} <button onclick="removeCountryTag('${country}'); event.stopPropagation();">×</button>`;
                tagsContainer.appendChild(tag);
            });
            
            filterTable();
        }
        
        // Remove country tag
        function removeCountryTag(country) {
            const checkbox = document.getElementById(`country-${country}`);
            if (checkbox) checkbox.checked = false;
            updateCountryFilter();
        }
        
        // Switch partition tabs
        let currentPartition = 'aws'; // Track current partition
        
        function switchPartition(partition) {
            // Update tab states
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById(`tab-${partition}`).classList.add('active');
            
            // Update map view
            if (partition === 'aws-eusc') {
                map.setView([50, 10], 4); // Zoom to Europe
            } else if (partition === 'aws-cn') {
                map.setView([35, 105], 4); // Zoom to China
            } else {
                map.setView([20, 0], 2); // Reset to world view
            }
            
            // Clear filters and update data
            clearAllCountries();
            document.getElementById('orgFilter').value = '';
            document.getElementById('regionFilter').value = '';
            document.getElementById('speedFilter').value = '';
            document.getElementById('macsecFilter').value = '';
            
            // Only repopulate filters if switching between different partitions
            const needsRepopulate = (partition === 'aws-eusc' || partition === 'aws-cn' || currentPartition === 'aws-eusc' || currentPartition === 'aws-cn');
            
            if (needsRepopulate) {
                const filterPartition = (partition === 'aws-eusc') ? 'aws-eusc' : (partition === 'aws-cn') ? 'aws-cn' : 'aws';
                populateFilters(filterPartition);
            }
            
            currentPartition = partition;
            filterTable();
        }
        
        // Get current partition
        function getCurrentPartition() {
            return document.querySelector('.tab.active').id.replace('tab-', '');
        }
        
        // Filter table and map
        function filterTable() {
            const searchInput = document.getElementById("searchInput").value.toUpperCase();
            const partitionFilter = getCurrentPartition();
            const orgFilter = document.getElementById("orgFilter").value;
            const regionFilter = document.getElementById("regionFilter").value;
            const speedFilter = document.getElementById("speedFilter").value;
            const macsecFilter = document.getElementById("macsecFilter").value;
            
            // Clear user marker and search if any filter is active
            if (selectedCountries.size > 0 || orgFilter || regionFilter || speedFilter || macsecFilter) {
                clearUserMarker();
                if (searchInput) {
                    document.getElementById('searchInput').value = '';
                    toggleClearBtn();
                }
            }
            
            // Re-read search input after potential clearing
            const finalSearchInput = document.getElementById("searchInput").value.toUpperCase();
            const table = document.getElementById("dxTable");
            const tr = table.getElementsByTagName("tr");
            const visibleCodes = new Set();
            
            // Show/hide reset button
            const resetBtn = document.getElementById('resetFilters');
            resetBtn.style.display = (selectedCountries.size > 0 || orgFilter || regionFilter || speedFilter || macsecFilter) ? 'block' : 'none';
            
            for (let i = 1; i < tr.length; i++) {
                const row = tr[i];
                const partition = row.dataset.partition || 'aws';
                const country = row.dataset.country || '';
                const org = row.dataset.org || '';
                const region = row.dataset.region || '';
                const speeds = row.dataset.speeds || '';
                const macsec = row.dataset.macsec || '';
                
                // Partition filter (always applied)
                // Commercial and GovCloud use the same data (aws partition)
                const effectivePartition = (partitionFilter === 'aws-govcloud') ? 'aws' : partitionFilter;
                const partitionMatch = partition === effectivePartition;
                
                // Text search
                let textMatch = true;
                if (finalSearchInput) {
                    const tds = row.getElementsByTagName("td");
                    textMatch = false;
                    for (let j = 0; j < tds.length; j++) {
                        const txtValue = tds[j].textContent || tds[j].innerText;
                        if (txtValue.toUpperCase().indexOf(finalSearchInput) > -1) {
                            textMatch = true;
                            break;
                        }
                    }
                }
                
                // Country filter (multi-select)
                const countryMatch = selectedCountries.size === 0 || selectedCountries.has(country);
                
                // Organization filter
                const orgMatch = !orgFilter || org === orgFilter;
                
                // Region filter
                const regionMatch = !regionFilter || region === regionFilter;
                
                // Speed filter
                let speedMatch = true;
                if (speedFilter) {
                    if (macsecFilter === 'macsec') {
                        speedMatch = macsec.includes(speedFilter);
                    } else if (macsecFilter === 'no-macsec') {
                        speedMatch = speeds.includes(speedFilter) && !macsec.includes(speedFilter);
                    } else {
                        speedMatch = speeds.includes(speedFilter) || macsec.includes(speedFilter);
                    }
                }
                
                // MACsec filter (when no speed selected)
                let macsecMatch = true;
                if (!speedFilter && macsecFilter) {
                    if (macsecFilter === 'macsec') {
                        macsecMatch = macsec.length > 0;
                    } else if (macsecFilter === 'no-macsec') {
                        macsecMatch = speeds.length > 0;
                    }
                }
                
                const show = partitionMatch && textMatch && countryMatch && orgMatch && regionMatch && speedMatch && macsecMatch;
                row.style.display = show ? "" : "none";
                if (show) {
                    visibleCodes.add(row.getAttribute('data-code'));
                }
            }
            
            // Update location count
            const locationCount = document.getElementById('locationCount');
            locationCount.textContent = `${visibleCodes.size} location${visibleCodes.size !== 1 ? 's' : ''}`;
            locationCount.style.display = 'block';
            
            // Update map markers
            Object.keys(markers).forEach(code => {
                if (visibleCodes.has(code)) {
                    map.addLayer(markers[code]);
                    map.addLayer(labels[code]);
                } else {
                    map.removeLayer(markers[code]);
                    map.removeLayer(labels[code]);
                }
            });
        }
    </script>
    <script>
        // Initialize after all functions are defined
        filterTable();
        currentSort = { col: 0, dir: 'asc' };
        document.getElementById('th0').classList.add('asc');
    </script>
    <div class="footer">
        <p><a href="https://github.com/chriselsen/dx-location-details" target="_blank">GitHub Repository</a> | Last updated: """ + datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC') + """</p>
    </div>
</body>
</html>
"""

# Write file
with open('docs/index.html', 'w') as f:
    f.write(html)

print("Generated docs/index.html")
