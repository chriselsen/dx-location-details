#!/usr/bin/env python3
import json

# Read the data
with open('data-structures/dx-locations-data.json', 'r') as f:
    locations = json.load(f)

# Read the icon
with open('icons/icon.txt', 'r') as f:
    icon_data = f.read().strip()

# Read region mapping
with open('data-structures/region-mapping.json', 'r') as f:
    region_mapping = json.load(f)

# Sort by region, then by name
sorted_locations = sorted(locations, key=lambda x: (x['region'], x['name']))

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
        .filters {{ display: flex; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }}
        .filters select {{ padding: 8px 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 14px; background: white; cursor: pointer; }}
        .filters select:hover {{ border-color: #999; }}
        .reset-filters {{ padding: 8px 16px; border: 2px solid #ddd; border-radius: 4px; font-size: 14px; background: white; cursor: pointer; display: none; }}
        .reset-filters:hover {{ background: #f0f0f0; border-color: #999; }}
        .search-container {{ position: relative; margin-bottom: 15px; }}
        #searchInput {{ width: 100%; padding: 12px 40px 12px 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 16px; box-sizing: border-box; }}
        .clear-btn {{ position: absolute; right: 10px; top: 50%; transform: translateY(-50%); background: none; border: none; font-size: 20px; cursor: pointer; color: #999; display: none; }}
        .clear-btn:hover {{ color: #333; }}
        table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th {{ background: #232f3e; color: white; padding: 12px; text-align: left; cursor: pointer; user-select: none; position: relative; }}
        th:hover {{ background: #37475a; }}
        th.asc::after {{ content: ' ▲'; position: absolute; right: 10px; }}
        th.desc::after {{ content: ' ▼'; position: absolute; right: 10px; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tbody tr {{ cursor: pointer; }}
        tr:hover {{ background: #f9f9f9; }}
        a {{ color: #0073bb; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .info-icon {{ display: inline-block; width: 16px; height: 16px; line-height: 16px; text-align: center; background: #0073bb; color: white; border-radius: 50%; font-size: 12px; font-weight: bold; margin-left: 5px; cursor: help; position: relative; }}
        .info-icon:hover::after {{ content: attr(data-tooltip); position: absolute; bottom: 125%; left: 50%; transform: translateX(-50%); background: #333; color: white; padding: 8px 12px; border-radius: 4px; white-space: normal; width: 300px; font-size: 13px; font-weight: normal; z-index: 1000; line-height: 1.4; }}
        .info-icon:hover::before {{ content: ''; position: absolute; bottom: 115%; left: 50%; transform: translateX(-50%); border: 6px solid transparent; border-top-color: #333; }}
    </style>
</head>
<body>
    <h1><img src="{icon_data}" alt="AWS Direct Connect">AWS Direct Connect Locations</h1>
    <div id="map">
        <button class="home-button" onclick="resetMap(); event.stopPropagation();" title="Reset map view">🏠</button>
    </div>
    <div class="filters">
        <select id="countryFilter" onchange="filterTable()">
            <option value="">All Countries</option>
        </select>
        <select id="speedFilter" onchange="filterTable()">
            <option value="">All Port Speeds</option>
        </select>
        <select id="macsecFilter" onchange="filterTable()">
            <option value="">All (MACsec & Non-MACsec)</option>
            <option value="macsec">With MACsec</option>
            <option value="no-macsec">Without MACsec</option>
        </select>
        <button class="reset-filters" id="resetFilters" onclick="resetFilters()">Reset Filters</button>
    </div>
    <div class="search-container">
        <input type="text" id="searchInput" placeholder="Search locations..." onkeyup="filterTable()" oninput="toggleClearBtn()">
        <button class="clear-btn" id="clearBtn" onclick="clearSearch()">✕</button>
    </div>
    <table id="dxTable">
        <thead>
            <tr>
                <th onclick="sortTable(0)" id="th0">Location</th>
                <th onclick="sortTable(1)" id="th1">Port Speeds</th>
                <th onclick="sortTable(2)" id="th2">Code</th>
                <th onclick="sortTable(3)" id="th3">Associated Region<span class="info-icon" data-tooltip="The AWS region used for API calls to manage Direct Connect resources at this location. Virtual interfaces created at this location can connect to any AWS region globally. Note: Opt-in regions must be enabled in your AWS account before locations in those regions become selectable." onclick="event.stopPropagation()">i</span></th>
            </tr>
        </thead>
        <tbody>
"""

# Add table rows with data attributes
for loc in sorted_locations:
    pdb_link = f"<a href='https://www.peeringdb.com/fac/{loc['peeringdb_id']}' target='_blank'>{loc['name']}</a>" if loc.get('peeringdb_id') else loc['name']
    
    speeds_unlocked = ', '.join(loc.get('port_speeds', []))
    speeds_macsec = ', '.join(loc.get('macsec_capable', []))
    speeds_html = f"<span title='Without MACsec'><svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align: middle;'><path stroke='none' d='M0 0h24v24H0z' fill='none'/><path d='M3 13a2 2 0 0 1 2 -2h10a2 2 0 0 1 2 2v6a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2l0 -6' /><path d='M9 16a1 1 0 1 0 2 0a1 1 0 0 0 -2 0' /><path d='M13 11v-4a4 4 0 1 1 8 0v4' /></svg></span> {speeds_unlocked}" if speeds_unlocked else ""
    if speeds_macsec:
        speeds_html += f"<br><span title='With MACsec'><svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' style='vertical-align: middle;'><path d='M5 13a2 2 0 0 1 2 -2h10a2 2 0 0 1 2 2v6a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2z' /><path d='M11 16a1 1 0 1 0 2 0a1 1 0 0 0 -2 0' /><path d='M8 11v-4a4 4 0 1 1 8 0v4' /></svg></span> {speeds_macsec}"
    
    if loc.get('latitude') and loc.get('longitude'):
        map_link = f"<a href='https://maps.google.com/?q={loc['latitude']},{loc['longitude']}' target='_blank'>{loc['code']}</a>"
    else:
        map_link = loc['code']
    
    region_name = region_mapping.get('aws_region_names', {}).get(loc['region'], loc['region'])
    region_html = f"{region_name}<br><code>{loc['region']}</code>"
    
    # Data attributes for filtering
    country = loc.get('country', '')
    port_speeds = ','.join(loc.get('port_speeds', []))
    macsec_speeds = ','.join(loc.get('macsec_capable', []))
    
    html += f"""            <tr data-code="{loc['code']}" data-country="{country}" data-speeds="{port_speeds}" data-macsec="{macsec_speeds}">
                <td>{pdb_link}</td>
                <td>{speeds_html}</td>
                <td>{map_link}</td>
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
        const speeds = new Set();
        document.querySelectorAll('tr[data-country]').forEach(tr => {
            if (tr.dataset.country) countries.add(tr.dataset.country);
            if (tr.dataset.speeds) tr.dataset.speeds.split(',').forEach(s => speeds.add(s));
            if (tr.dataset.macsec) tr.dataset.macsec.split(',').forEach(s => speeds.add(s));
        });
        
        Array.from(countries).sort().forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            document.getElementById('countryFilter').appendChild(opt);
        });
        
        Array.from(speeds).sort((a,b) => {
            const order = {'1G':1, '10G':2, '100G':3, '400G':4};
            return (order[a]||99) - (order[b]||99);
        }).forEach(s => {
            const opt = document.createElement('option');
            opt.value = s;
            opt.textContent = s;
            document.getElementById('speedFilter').appendChild(opt);
        });
        
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
            map.setView([20, 0], 2);
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
            document.getElementById('countryFilter').value = '';
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
            document.getElementById('countryFilter').value = '';
            document.getElementById('speedFilter').value = '';
            document.getElementById('macsecFilter').value = '';
            filterTable();
        }
        
        // Filter table and map
        function filterTable() {
            clearUserMarker();
            const searchInput = document.getElementById("searchInput").value.toUpperCase();
            const countryFilter = document.getElementById("countryFilter").value;
            const speedFilter = document.getElementById("speedFilter").value;
            const macsecFilter = document.getElementById("macsecFilter").value;
            
            // Clear search box if any filter is active
            if (countryFilter || speedFilter || macsecFilter) {
                document.getElementById('searchInput').value = '';
                toggleClearBtn();
            }
            const table = document.getElementById("dxTable");
            const tr = table.getElementsByTagName("tr");
            const visibleCodes = new Set();
            
            // Show/hide reset button
            const resetBtn = document.getElementById('resetFilters');
            resetBtn.style.display = (countryFilter || speedFilter || macsecFilter) ? 'block' : 'none';
            
            for (let i = 1; i < tr.length; i++) {
                const row = tr[i];
                const country = row.dataset.country || '';
                const speeds = row.dataset.speeds || '';
                const macsec = row.dataset.macsec || '';
                
                // Text search
                let textMatch = true;
                if (searchInput) {
                    const tds = row.getElementsByTagName("td");
                    textMatch = false;
                    for (let j = 0; j < tds.length; j++) {
                        const txtValue = tds[j].textContent || tds[j].innerText;
                        if (txtValue.toUpperCase().indexOf(searchInput) > -1) {
                            textMatch = true;
                            break;
                        }
                    }
                }
                
                // Country filter
                const countryMatch = !countryFilter || country === countryFilter;
                
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
                
                const show = textMatch && countryMatch && speedMatch && macsecMatch;
                row.style.display = show ? "" : "none";
                if (show) {
                    visibleCodes.add(row.getAttribute('data-code'));
                }
            }
            
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
</body>
</html>
"""

# Write file
with open('docs/index.html', 'w') as f:
    f.write(html)

print("Generated docs/index.html")
