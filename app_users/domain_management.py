"""
Domain management for user registration
Handles whitelist for auto-approval and blocklist for rejection
"""

from django.core.cache import cache
from .models import Domain


def get_cached_domain_lists():
    """
    Get domain lists from cache or database
    """
    cache_key = "domain_management_lists"
    cached_data = cache.get(cache_key)

    if cached_data is None:
        try:
            domain_obj = Domain.get_or_create_domain_management()
            cached_data = {
                "whitelisted": set(domain_obj.whitelisted_domains or []),
                "blocklisted": set(domain_obj.blocklisted_domains or []),
            }
            # Cache for 1 hour
            cache.set(cache_key, cached_data, 3600)
        except Exception:
            # Fallback to empty sets if database is not available
            cached_data = {"whitelisted": set(), "blocklisted": set()}

    return cached_data


def clear_domain_cache():
    """
    Clear the domain management cache
    """
    cache.delete("domain_management_lists")


# Legacy constants for backward compatibility (deprecated)
# These will be removed in future versions
WHITELISTED_DOMAINS = set()
BLOCKLISTED_DOMAINS = set()

# Initialize legacy constants from database
try:
    domain_obj = Domain.get_or_create_domain_management()
    WHITELISTED_DOMAINS = set(domain_obj.whitelisted_domains or [])
    BLOCKLISTED_DOMAINS = set(domain_obj.blocklisted_domains or [])
except Exception:
    pass


def get_email_domain(email):
    """
    Extract domain from email address

    Args:
        email (str): Email address

    Returns:
        str: Domain part of the email in lowercase
    """
    if not email or "@" not in email:
        return ""

    return email.split("@")[1].lower().strip()


def is_whitelisted_domain(email):
    """
    Check if email domain is in the whitelist for auto-approval

    Args:
        email (str): Email address to check

    Returns:
        bool: True if domain is whitelisted, False otherwise
    """
    domain = get_email_domain(email)
    domain_lists = get_cached_domain_lists()
    return domain in domain_lists["whitelisted"]


def is_blocklisted_domain(email):
    """
    Check if email domain is in the blocklist and should be rejected

    Args:
        email (str): Email address to check

    Returns:
        bool: True if domain is blocklisted, False otherwise
    """
    domain = get_email_domain(email)
    domain_lists = get_cached_domain_lists()
    return domain in domain_lists["blocklisted"]


def get_domain_status(email):
    """
    Get the status of an email domain

    Args:
        email (str): Email address to check

    Returns:
        str: 'whitelisted', 'blocklisted', or 'neutral'
    """
    if is_blocklisted_domain(email):
        return "blocklisted"
    elif is_whitelisted_domain(email):
        return "whitelisted"
    else:
        return "neutral"


def should_auto_approve(email):
    """
    Determine if a user with this email should be auto-approved

    Args:
        email (str): Email address to check

    Returns:
        bool: True if user should be auto-approved, False otherwise
    """
    return is_whitelisted_domain(email)


def should_block_registration(email):
    """
    Determine if registration should be blocked for this email

    Args:
        email (str): Email address to check

    Returns:
        bool: True if registration should be blocked, False otherwise
    """
    return is_blocklisted_domain(email)


def update_domain_lists(whitelisted_domains=None, blocklisted_domains=None):
    """
    Update domain lists in the database and clear cache

    Args:
        whitelisted_domains (list): New list of whitelisted domains
        blocklisted_domains (list): New list of blocklisted domains
    """
    try:
        domain_obj = Domain.get_or_create_domain_management()

        if whitelisted_domains is not None:
            domain_obj.whitelisted_domains = whitelisted_domains

        if blocklisted_domains is not None:
            domain_obj.blocklisted_domains = blocklisted_domains

        domain_obj.save()

        # Clear cache to force refresh
        clear_domain_cache()

        # Update legacy constants
        global WHITELISTED_DOMAINS, BLOCKLISTED_DOMAINS
        WHITELISTED_DOMAINS = set(domain_obj.whitelisted_domains or [])
        BLOCKLISTED_DOMAINS = set(domain_obj.blocklisted_domains or [])

        return True
    except Exception as e:
        return False
