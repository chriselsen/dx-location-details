#!/usr/bin/env python3
import json

def get_region_name(region_code):
    """Convert region code to friendly name"""
    region_names = {
        'us-east-1': 'US East (N. Virginia)', 'us-east-2': 'US East (Ohio)',
        'us-west-1': 'US West (N. California)', 'us-west-2': 'US West (Oregon)',
        'af-south-1': 'Africa (Cape Town)', 'ap-east-1': 'Asia Pacific (Hong Kong)',
        'ap-south-1': 'Asia Pacific (Mumbai)', 'ap-northeast-2': 'Asia Pacific (Seoul)',
        'ap-southeast-1': 'Asia Pacific (Singapore)', 'ap-southeast-2': 'Asia Pacific (Sydney)',
        'ap-southeast-3': 'Asia Pacific (Jakarta)', 'ap-southeast-4': 'Asia Pacific (Melbourne)',
        'ap-southeast-5': 'Asia Pacific (Malaysia)', 'ap-southeast-6': 'Asia Pacific (New Zealand)',
        'ap-southeast-7': 'Asia Pacific (Thailand)', 'ap-northeast-1': 'Asia Pacific (Tokyo)',
        'ap-northeast-3': 'Asia Pacific (Osaka)', 'ap-east-2': 'Asia Pacific (Taipei)',
        'ca-central-1': 'Canada (Central)', 'ca-west-1': 'Canada (Calgary)',
        'eu-central-1': 'Europe (Frankfurt)', 'eu-west-1': 'Europe (Ireland)',
        'eu-west-2': 'Europe (London)', 'eu-west-3': 'Europe (Paris)',
        'eu-north-1': 'Europe (Stockholm)', 'eu-south-1': 'Europe (Milan)',
        'eu-south-2': 'Europe (Spain)', 'eu-central-2': 'Europe (Zurich)',
        'il-central-1': 'Israel (Tel Aviv)', 'me-south-1': 'Middle East (Bahrain)',
        'me-central-1': 'Middle East (UAE)', 'sa-east-1': 'South America (São Paulo)',
        'cn-north-1': 'China (Beijing)', 'cn-northwest-1': 'China (Ningxia)',
        'mx-central-1': 'Mexico (Central)'
    }
    return region_names.get(region_code, region_code)

def generate_github_table(data):
    """Generate GitHub-compatible markdown table with sortable functionality"""
    output = []
    output.append("# AWS Direct Connect Locations\n")
    output.append("This table lists all AWS Direct Connect locations worldwide.\n")
    output.append("<input type='text' id='searchInput' onkeyup='filterTable()' placeholder='Search for locations...' style='width:100%;padding:8px;margin-bottom:10px;'>\n")
    output.append("<table id=\"dxTable\">")
    output.append("<thead>")
    output.append("<tr>")
    output.append("<th onclick=\"sortTable(0)\">DX Location ⇅</th>")
    output.append("<th onclick=\"sortTable(1)\">Port Speeds ⇅</th>")
    output.append("<th onclick=\"sortTable(2)\">Location Code ⇅</th>")
    output.append("<th onclick=\"sortTable(3)\">Associated AWS Region ⇅</th>")
    output.append("</tr>")
    output.append("</thead>")
    output.append("<tbody>")
    
    for entry in data:
        region_name = get_region_name(entry['region'])
        
        if entry.get('peeringdb_id'):
            location_link = f"<a href='https://www.peeringdb.com/fac/{entry['peeringdb_id']}'>{entry['name']}</a>"
        else:
            location_link = entry['name']
        
        port_speeds_parts = []
        if entry.get('port_speeds'):
            port_speeds_parts.append('🔓 ' + ', '.join(entry['port_speeds']))
        if entry.get('macsec_capable'):
            port_speeds_parts.append('🔒 ' + ', '.join(entry['macsec_capable']))
        port_speeds_str = '<br>'.join(port_speeds_parts) if port_speeds_parts else 'N/A'
        
        if entry.get('latitude') and entry.get('longitude'):
            lat, lon = entry['latitude'], entry['longitude']
            location_code_link = f"<a href='https://maps.google.com/?q={lat},{lon}'>{entry['code']}</a>"
        else:
            location_code_link = entry['code']
        
        region_display = f"{region_name}<br><code>{entry['region']}</code>"
        
        output.append("<tr>")
        output.append(f"<td>{location_link}</td>")
        output.append(f"<td>{port_speeds_str}</td>")
        output.append(f"<td>{location_code_link}</td>")
        output.append(f"<td>{region_display}</td>")
        output.append("</tr>")
    
    output.append("</tbody>")
    output.append("</table>\n")
    output.append("<script>")
    output.append("function sortTable(n) {")
    output.append("  var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;")
    output.append("  table = document.getElementById('dxTable');")
    output.append("  switching = true;")
    output.append("  dir = 'asc';")
    output.append("  while (switching) {")
    output.append("    switching = false;")
    output.append("    rows = table.rows;")
    output.append("    for (i = 1; i < (rows.length - 1); i++) {")
    output.append("      shouldSwitch = false;")
    output.append("      x = rows[i].getElementsByTagName('TD')[n];")
    output.append("      y = rows[i + 1].getElementsByTagName('TD')[n];")
    output.append("      if (dir == 'asc') {")
    output.append("        if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {")
    output.append("          shouldSwitch = true;")
    output.append("          break;")
    output.append("        }")
    output.append("      } else if (dir == 'desc') {")
    output.append("        if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {")
    output.append("          shouldSwitch = true;")
    output.append("          break;")
    output.append("        }")
    output.append("      }")
    output.append("    }")
    output.append("    if (shouldSwitch) {")
    output.append("      rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);")
    output.append("      switching = true;")
    output.append("      switchcount ++;")
    output.append("    } else {")
    output.append("      if (switchcount == 0 && dir == 'asc') {")
    output.append("        dir = 'desc';")
    output.append("        switching = true;")
    output.append("      }")
    output.append("    }")
    output.append("  }")
    output.append("}")
    output.append("</script>")
    output.append("<script>")
    output.append("function filterTable() {")
    output.append("  var input, filter, table, tr, td, i, j, txtValue;")
    output.append("  input = document.getElementById('searchInput');")
    output.append("  filter = input.value.toLowerCase();")
    output.append("  table = document.getElementById('dxTable');")
    output.append("  tr = table.getElementsByTagName('tr');")
    output.append("  for (i = 1; i < tr.length; i++) {")
    output.append("    tr[i].style.display = 'none';")
    output.append("    td = tr[i].getElementsByTagName('td');")
    output.append("    for (j = 0; j < td.length; j++) {")
    output.append("      if (td[j]) {")
    output.append("        txtValue = td[j].textContent || td[j].innerText;")
    output.append("        if (txtValue.toLowerCase().indexOf(filter) > -1) {")
    output.append("          tr[i].style.display = '';")
    output.append("          break;")
    output.append("        }")
    output.append("      }")
    output.append("    }")
    output.append("  }")
    output.append("}")
    output.append("</script>")
    
    return '\n'.join(output)

def main():
    data_file = 'data-structures/dx-locations-data.json'
    output_file = 'output/DX_LOCATIONS.md'
    
    print("Loading data...")
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print("Generating GitHub markdown table...")
    table = generate_github_table(data)
    
    with open(output_file, 'w') as f:
        f.write(table)
    
    print(f"GitHub markdown table generated: {output_file}")

if __name__ == '__main__':
    main()
