#!/usr/bin/env python3
import json
import folium
from PIL import Image
import io

def generate_map():
    with open('data-structures/dx-locations-data.json', 'r') as f:
        locations = json.load(f)
    
    # Create map centered on world
    m = folium.Map(location=[20, 0], zoom_start=2, tiles='OpenStreetMap')
    
    # Add markers
    for loc in locations:
        if loc.get('latitude') and loc.get('longitude'):
            folium.CircleMarker(
                location=[float(loc['latitude']), float(loc['longitude'])],
                radius=4,
                popup=f"{loc['code']}: {loc['name']}",
                color='#FF6600',
                fill=True,
                fillColor='#FF6600',
                fillOpacity=0.8
            ).add_to(m)
    
    # Save as HTML first
    m.save('output/DX_Locations_map.html')
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
