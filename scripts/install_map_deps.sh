#!/bin/bash
# Install dependencies for generating DX_Locations.png map

echo "Installing Python dependencies for map generation..."

# Install matplotlib, cartopy, and boto3
pip3 install matplotlib cartopy boto3

echo "✓ Dependencies installed successfully"
echo ""
echo "You can now run: python3 scripts/generate_map_png.py"
