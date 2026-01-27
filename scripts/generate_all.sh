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

echo "Step 2: Generating markdown table..."
python3 scripts/generate_github_md.py
echo ""

echo "Step 3: Generating KML files..."
python3 scripts/generate_kml.py
echo ""

echo "Step 4: Generating world map PNG..."
python3 scripts/generate_map_png.py
echo ""

echo "=========================================="
echo "✓ All outputs generated successfully!"
echo "=========================================="
