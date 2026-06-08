#!/bin/bash
# Runs all output generation steps for all partitions

set -e  # Exit on error

echo "=========================================="
echo "DX Location Details - Generate All Outputs"
echo "=========================================="
echo ""

echo "Step 1: Generating CSV files..."
python3 scripts/generate_csv.py
python3 scripts/generate_csv_eusc.py
python3 scripts/generate_csv_china.py
echo ""

echo "Step 2: Generating KML files..."
python3 scripts/generate_kml.py
python3 scripts/generate_kml_eusc.py
python3 scripts/generate_kml_china.py
echo ""

echo "Step 3: Generating world map PNG..."
python3 scripts/generate_map_png.py
echo ""

echo "Step 4: Generating GitHub Pages..."
python3 scripts/generate_github_pages.py
python3 scripts/generate_locations_json.py
echo ""

echo "=========================================="
echo "✓ All outputs generated successfully!"
echo "=========================================="
