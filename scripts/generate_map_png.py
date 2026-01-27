#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def generate_map_png():
    with open('data-structures/dx-locations-data.json', 'r') as f:
        locations = json.load(f)
    
    fig = plt.figure(figsize=(20, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    ax.add_feature(cfeature.LAND, facecolor='#E8E8E8')
    ax.add_feature(cfeature.OCEAN, facecolor='#B8D4E8')
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)
    
    lons = [float(loc['longitude']) for loc in locations if loc.get('latitude') and loc.get('longitude')]
    lats = [float(loc['latitude']) for loc in locations if loc.get('latitude') and loc.get('longitude')]
    
    ax.scatter(lons, lats, c='#FF6600', s=40, alpha=0.9, edgecolors='#CC5200', linewidth=1, 
               transform=ccrs.PlateCarree(), zorder=5)
    
    ax.set_global()
    ax.gridlines(draw_labels=False, linewidth=0.5, alpha=0.3, linestyle='--')
    plt.title('AWS Direct Connect Locations', fontsize=18, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('output/DX_Locations.png', dpi=150, bbox_inches='tight')
    print(f"Generated: output/DX_Locations.png ({len(lons)} locations)")
    plt.close()

if __name__ == '__main__':
    generate_map_png()
