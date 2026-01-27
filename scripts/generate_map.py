#!/usr/bin/env python3
import json
import folium
from PIL import Image
import io
import base64

def generate_map():
    with open('data-structures/dx-locations-data.json', 'r') as f:
        locations = json.load(f)
    
    # Read the custom icon
    with open('icons/icon.txt', 'r') as f:
        icon_data = f.read().strip()
    
    # Create map centered on world
    m = folium.Map(location=[20, 0], zoom_start=2, tiles='OpenStreetMap')
    
    # Add markers with custom icon and labels
    for loc in locations:
        if loc.get('latitude') and loc.get('longitude'):
            # Create custom icon
            icon = folium.CustomIcon(
                icon_image=icon_data,
                icon_size=(24, 24)
            )
            
            # Add marker with icon
            folium.Marker(
                location=[float(loc['latitude']), float(loc['longitude'])],
                popup=f"{loc['code']}: {loc['name']}",
                icon=icon,
                tooltip=loc['code']  # This adds the DX code as a label on hover
            ).add_to(m)
            
            # Add permanent label for DX code
            folium.Marker(
                location=[float(loc['latitude']), float(loc['longitude'])],
                icon=folium.DivIcon(html=f'<div style="font-size: 10px; font-weight: bold; color: #232f3e; text-shadow: 1px 1px 2px white, -1px -1px 2px white, 1px -1px 2px white, -1px 1px 2px white; white-space: nowrap; margin-top: 20px;">{loc["code"]}</div>')
            ).add_to(m)
    
    # Save as HTML first
    m.save('output/DX_Locations_map.html')
    
    # Add favicon to the generated HTML
    with open('output/DX_Locations_map.html', 'r') as f:
        html_content = f.read()
    
    favicon_tag = f'<link rel="icon" type="image/jpeg" href="{icon_data}">'
    html_content = html_content.replace('<head>', f'<head>\n    {favicon_tag}')
    
    with open('output/DX_Locations_map.html', 'w') as f:
        f.write(html_content)
    
    print("Generated: output/DX_Locations_map.html")
    
    # Try to save as PNG using selenium if available
    try:
        import selenium.webdriver as webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1920, 1080)
        driver.get(f'file://{os.path.abspath("output/DX_Locations_map.html")}')
        driver.save_screenshot('output/DX_Locations.png')
        driver.quit()
        print("Generated: output/DX_Locations.png")
    except:
        print("Note: Install Chrome/ChromeDriver for PNG generation. HTML map created.")

if __name__ == '__main__':
    generate_map()
