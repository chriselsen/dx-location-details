#!/bin/bash
# Weekly generation script - runs all output generation steps

set -e  # Exit on error

echo "=========================================="
echo "DX Location Details - Weekly Generation"
echo "=========================================="
echo ""

echo "Step 1: Collecting data from AWS..."
python3 scripts/collect_data.py
echo ""

echo "Step 2: Generating CSV files..."
python3 scripts/generate_csv.py
if [ -f "data-structures/dx-locations-data-eusc.json" ]; then
    python3 scripts/generate_csv_eusc.py
fi
echo ""

echo "Step 3: Generating KML files..."
python3 scripts/generate_kml.py
if [ -f "data-structures/dx-locations-data-eusc.json" ]; then
    python3 scripts/generate_kml_eusc.py
fi
echo ""

echo "Step 4: Generating world map PNG..."
python3 scripts/generate_map_png.py
echo ""

echo "Step 5: Generating GitHub Pages..."
python3 scripts/generate_github_pages.py
echo ""

echo "=========================================="
echo "✓ All outputs generated successfully!"
echo "=========================================="
