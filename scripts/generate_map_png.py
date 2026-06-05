#!/usr/bin/env python3
import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from PIL import Image

def generate_map_png():
    with open('data-structures/dx-locations-data.json', 'r', encoding='utf-8') as f:
        locations = json.load(f)

    with open('icons/icon.txt', 'r', encoding='utf-8') as f:
        icon_data = f.read().strip()
    raw_b64 = icon_data.split(',', 1)[1] if ',' in icon_data else icon_data
    icon_img = Image.open(BytesIO(base64.b64decode(raw_b64)))
    icon_img = icon_img.resize((14, 14), Image.LANCZOS)

    fig = plt.figure(figsize=(20, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND, facecolor='#E8E8E8')
    ax.add_feature(cfeature.OCEAN, facecolor='#B8D4E8')
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linewidth=0.3, alpha=0.5)

    coords = [(float(loc['longitude']), float(loc['latitude']))
              for loc in locations if loc.get('latitude') and loc.get('longitude')]

    for lon, lat in coords:
        im = OffsetImage(icon_img, zoom=1.0)
        ab = AnnotationBbox(im, (lon, lat), frameon=False,
                            xycoords=ccrs.PlateCarree()._as_mpl_transform(ax))
        ax.add_artist(ab)

    ax.set_global()
    ax.gridlines(draw_labels=False, linewidth=0.5, alpha=0.3, linestyle='--')
    plt.title('AWS Direct Connect Locations', fontsize=18, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig('output/DX_Locations.png', dpi=150, bbox_inches='tight')
    print(f"Generated: output/DX_Locations.png ({len(coords)} locations)")
    plt.close()

if __name__ == '__main__':
    generate_map_png()
