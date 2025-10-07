"""
Custom template tags for loading data
Similar to Next.js data fetching in components
"""

from django import template
from bitbio.utils.data_loader import load_json_data, get_navigation_data

register = template.Library()


@register.simple_tag
def load_data(filename):
    """
    Load any JSON data file in templates
    Usage: {% load_data 'navigation.json' as nav_data %}
    """
    return load_json_data(filename)


@register.simple_tag
def get_nav_data():
    """
    Get navigation data specifically
    Usage: {% get_nav_data as navigation %}
    """
    return get_navigation_data()
