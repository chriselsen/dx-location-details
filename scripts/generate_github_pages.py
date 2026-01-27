#!/usr/bin/env python3
import json
import shutil

# Read the data
with open('data-structures/dx-locations-data.json', 'r') as f:
    locations = json.load(f)

# Generate table HTML
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS Direct Connect Locations</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        h1 { color: #232f3e; }
        #searchInput { width: 100%; padding: 12px; margin-bottom: 15px; border: 2px solid #ddd; border-radius: 4px; font-size: 16px; }
        table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        th { background: #232f3e; color: white; padding: 12px; text-align: left; cursor: pointer; user-select: none; position: relative; }
        th:hover { background: #37475a; }
        th.asc::after { content: ' ▲'; position: absolute; right: 10px; }
        th.desc::after { content: ' ▼'; position: absolute; right: 10px; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        tr:hover { background: #f9f9f9; }
        a { color: #0073bb; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>AWS Direct Connect Locations</h1>
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

# Sort by region, then by name
sorted_locations = sorted(locations, key=lambda x: (x['region'], x['name']))

for loc in sorted_locations:
    pdb_link = f"<a href='https://www.peeringdb.com/fac/{loc['peeringdb_id']}' target='_blank'>{loc['name']}, {loc['country']}</a>" if loc.get('peeringdb_id') else f"{loc['name']}, {loc['country']}"
    
    # Port speeds
    speeds_unlocked = ', '.join(loc.get('port_speeds', []))
    speeds_macsec = ', '.join(loc.get('macsec_capable', []))
    speeds_html = f"<span title='Without MACsec'>🔓</span> {speeds_unlocked}" if speeds_unlocked else ""
    if speeds_macsec:
        speeds_html += f"<br><span title='With MACsec'>🔒</span> {speeds_macsec}"
    
    # Map link
    if loc.get('latitude') and loc.get('longitude'):
        map_link = f"<a href='https://maps.google.com/?q={loc['latitude']},{loc['longitude']}' target='_blank'>{loc['code']}</a>"
    else:
        map_link = loc['code']
    
    # Region name
    with open('data-structures/region-mapping.json', 'r') as f:
        regions = json.load(f)
    region_name = regions.get('aws_region_names', {}).get(loc['region'], loc['region'])
    region_html = f"{region_name}<br><code>{loc['region']}</code>"
    
    html_content += f"""            <tr>
                <td>{pdb_link}</td>
                <td>{speeds_html}</td>
                <td>{map_link}</td>
                <td>{region_html}</td>
            </tr>
"""

html_content += """        </tbody>
    </table>
    <script>
        let currentSort = { col: -1, dir: 'asc' };
        
        function sortTable(n) {
            const table = document.getElementById("dxTable");
            const tbody = table.tBodies[0];
            const rows = Array.from(tbody.rows);
            
            // Toggle direction
            if (currentSort.col === n) {
                currentSort.dir = currentSort.dir === 'asc' ? 'desc' : 'asc';
            } else {
                currentSort.col = n;
                currentSort.dir = 'asc';
            }
            
            // Sort rows
            rows.sort((a, b) => {
                const aText = a.cells[n].textContent.trim();
                const bText = b.cells[n].textContent.trim();
                const compare = aText.localeCompare(bText, undefined, { numeric: true });
                return currentSort.dir === 'asc' ? compare : -compare;
            });
            
            // Reorder rows
            rows.forEach(row => tbody.appendChild(row));
            
            // Update headers
            document.querySelectorAll('th').forEach(th => {
                th.classList.remove('asc', 'desc');
            });
            document.getElementById('th' + n).classList.add(currentSort.dir);
        }
        
        function filterTable() {
            const input = document.getElementById("searchInput");
            const filter = input.value.toUpperCase();
            const table = document.getElementById("dxTable");
            const tr = table.getElementsByTagName("tr");
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
            }
        }
    </script>
</body>
</html>
"""

# Write table HTML
with open('docs/index.html', 'w') as f:
    f.write(html_content)

# Copy map HTML
shutil.copy('output/DX_Locations_map.html', 'docs/map.html')

print("Generated docs/index.html and docs/map.html for GitHub Pages")
