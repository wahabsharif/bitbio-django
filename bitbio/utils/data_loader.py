"""
Utility functions for loading data files (similar to Next.js data management)
"""

import json
import os
from pathlib import Path
from django.conf import settings
from functools import lru_cache


@lru_cache(maxsize=None)
def load_json_data(filename):
    """
    Load JSON data file with caching
    Similar to importing data in Next.js

    Args:
        filename: Name of the JSON file (e.g., 'navigation.json')

    Returns:
        dict: Parsed JSON data
    """
    # Convert to string in case it's a Django SafeString
    # Force conversion to plain string to avoid Path operator issues
    if hasattr(filename, "__str__"):
        filename = filename.__str__()
    filename = str(filename)

    data_dir = Path(settings.BASE_DIR) / "bitbio" / "data"
    # Use string concatenation instead of Path operator for safety
    file_path = Path(str(data_dir) + "/" + str(filename))

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Data file {filename} not found at {file_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {filename}: {e}")
        return {}


def get_navigation_data():
    """
    Get navigation data
    Similar to Next.js: import navigationData from '@/data/header-data.json'
    """
    return load_json_data("header-data.json")


def clear_data_cache():
    """
    Clear cached data (useful in development or when data changes)
    """
    load_json_data.cache_clear()
