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
    <title>AWS Direct Connect Locations - Advanced View</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"/>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        h1 {{ color: #232f3e; }}
        #map {{ height: 500px; width: 100%; margin-bottom: 20px; border: 2px solid #ddd; border-radius: 4px; background: white; position: relative; }}
        .home-button {{ position: absolute; bottom: 10px; left: 10px; z-index: 1000; background: white; border: 2px solid #ccc; border-radius: 4px; padding: 8px 12px; cursor: pointer; font-size: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
        .home-button:hover {{ background: #f0f0f0; }}
        #searchInput {{ width: 100%; padding: 12px; margin-bottom: 15px; border: 2px solid #ddd; border-radius: 4px; font-size: 16px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th {{ background: #232f3e; color: white; padding: 12px; text-align: left; cursor: pointer; user-select: none; position: relative; }}
        th:hover {{ background: #37475a; }}
        th.asc::after {{ content: ' ▲'; position: absolute; right: 10px; }}
        th.desc::after {{ content: ' ▼'; position: absolute; right: 10px; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f9f9f9; }}
        a {{ color: #0073bb; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <h1>AWS Direct Connect Locations</h1>
    <div id="map">
        <button class="home-button" onclick="resetMap()" title="Reset map view">🏠</button>
    </div>
    <input type="text" id="searchInput" placeholder="Search locations..." onkeyup="filterTable()">
    <table id="dxTable">
        <thead>
            <tr>
                <th onclick="sortTable(0)" id="th0">Location</th>
                <th onclick="sortTable(1)" id="th1">Port Speeds</th>
                <th onclick="sortTable(2)" id="th2">Code</th>
                <th onclick="sortTable(3)" id="th3">Region</th>
            </tr>
        </thead>
        <tbody>
"""

# Add table rows
for loc in sorted_locations:
    pdb_link = f"<a href='https://www.peeringdb.com/fac/{loc['peeringdb_id']}' target='_blank'>{loc['name']}, {loc['country']}</a>" if loc.get('peeringdb_id') else f"{loc['name']}, {loc['country']}"
    
    speeds_unlocked = ', '.join(loc.get('port_speeds', []))
    speeds_macsec = ', '.join(loc.get('macsec_capable', []))
    speeds_html = f"<span title='Without MACsec'>🔓</span> {speeds_unlocked}" if speeds_unlocked else ""
    if speeds_macsec:
        speeds_html += f"<br><span title='With MACsec'>🔒</span> {speeds_macsec}"
    
    if loc.get('latitude') and loc.get('longitude'):
        map_link = f"<a href='https://maps.google.com/?q={loc['latitude']},{loc['longitude']}' target='_blank'>{loc['code']}</a>"
    else:
        map_link = loc['code']
    
    region_name = region_mapping.get('aws_region_names', {}).get(loc['region'], loc['region'])
    region_html = f"{region_name}<br><code>{loc['region']}</code>"
    
    html += f"""            <tr data-code="{loc['code']}">
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
        
"""

# Add markers
for loc in locations:
    if loc.get('latitude') and loc.get('longitude'):
        html += f"""        markers['{loc['code']}'] = L.marker([{loc['latitude']}, {loc['longitude']}], {{icon: customIcon}})
            .on('click', function(e) {{ L.DomEvent.stopPropagation(e); selectLocation('{loc['code']}'); }})
            .addTo(map);
        labels['{loc['code']}'] = L.marker([{loc['latitude']}, {loc['longitude']}], {{
            icon: L.divIcon({{html: '<div style="font-size: 10px; font-weight: bold; color: #232f3e; text-shadow: 1px 1px 2px white, -1px -1px 2px white, 1px -1px 2px white, -1px 1px 2px white; white-space: nowrap; margin-top: 20px;">{loc['code']}</div>', className: 'empty'}})
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
            selectedCode = code;
            document.getElementById('searchInput').value = code;
            filterTable();
        }
        
        // Clear selection on map click
        map.on('click', function() {
            selectedCode = null;
            document.getElementById('searchInput').value = '';
            filterTable();
        });
        
        // Reset map view
        function resetMap() {
            map.setView([20, 0], 2);
        }
        
        // Filter table and map
        function filterTable() {
            const input = document.getElementById("searchInput");
            const filter = input.value.toUpperCase();
            const table = document.getElementById("dxTable");
            const tr = table.getElementsByTagName("tr");
            const visibleCodes = new Set();
            
            for (let i = 1; i < tr.length; i++) {
                const tds = tr[i].getElementsByTagName("td");
                let found = false;
                for (let j = 0; j < tds.length; j++) {
                    const txtValue = tds[j].textContent || tds[j].innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        found = true;
                        break;
                    }
                }
                tr[i].style.display = found ? "" : "none";
                if (found) {
                    visibleCodes.add(tr[i].getAttribute('data-code'));
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
with open('docs/advanced.html', 'w') as f:
    f.write(html)

print("Generated docs/advanced.html")
