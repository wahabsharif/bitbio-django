"""
Context processors for making data available globally in templates
"""

from .utils.data_loader import load_json_data


def header_data(request):
    """
    Make header data available in all templates
    """
    return {"header_data": load_json_data("header-data.json")}


def site_config(request):
    """
    Add site-wide configuration data
    You can add more global data here as needed
    """
    return {
        "site_name": "bit.bio",
        "site_url": "https://www.bit.bio",
        "shop_url": "https://shop.bit.bio",
    }
