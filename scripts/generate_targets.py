#!/usr/bin/env python3
import json
from collections import defaultdict

def load_region_mapping():
    with open('data-structures/region-mapping.json', 'r') as f:
        return json.load(f)

def get_europe_region(country, europe_regions):
    """Get Europe sub-region for a country"""
    for region, countries in europe_regions.items():
        if country in countries:
            return region
    return None

def get_asia_region(country, asia_regions):
    """Get Asia sub-region for a country"""
    for region, countries in asia_regions.items():
        if country in countries:
            return region
    return None

def extract_city(name):
    """Extract city from location name (format: 'Facility, City, Country' or 'Facility City')"""  
    parts = [p.strip() for p in name.split(',')]
    if len(parts) >= 2:
        return parts[1]  # City is typically after first comma
    return name

def get_flag(country):
    """Get flag code for a country"""
    return country.lower() if country else 'xx'

def generate_targets():
    print("Note: Target generation requires internal IP addresses which are not available in the external version.")
    print("Skipping Targets.txt generation.")

if __name__ == '__main__':
    generate_targets()
