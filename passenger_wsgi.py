#!/usr/bin/env python3
"""
Passenger WSGI file for BitBio Django application.

This file is used by Passenger to serve the Django application.
Make sure to adjust the paths according to your server setup.

IMPORTANT: Before deploying to production, ensure Django is installed:
1. Activate virtual environment: source venv/bin/activate
2. Install dependencies: pip install -r requirements.txt
3. Run migrations: python manage.py migrate
4. Collect static files: python manage.py collectstatic
"""

import os
import sys

# Add the project directory to the Python path
# Adjust this path to match your server's directory structure
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Try to activate virtual environment if it exists
venv_path = os.path.join(project_dir, "venv")
if os.path.exists(venv_path):
    # For Windows environments
    site_packages = os.path.join(venv_path, "Lib", "site-packages")
    if os.path.exists(site_packages) and site_packages not in sys.path:
        sys.path.insert(0, site_packages)

    # For Linux/Unix environments
    site_packages_linux = os.path.join(venv_path, "lib", "python3.13", "site-packages")
    if os.path.exists(site_packages_linux) and site_packages_linux not in sys.path:
        sys.path.insert(0, site_packages_linux)

    # Also try alternative Python versions for Linux
    for python_version in [
        "python3.13",
        "python3.12",
        "python3.11",
        "python3.10",
        "python3.9",
    ]:
        alt_site_packages = os.path.join(
            venv_path, "lib", python_version, "site-packages"
        )
        if os.path.exists(alt_site_packages) and alt_site_packages not in sys.path:
            sys.path.insert(0, alt_site_packages)
            break

try:
    import django
    from django.core.wsgi import get_wsgi_application
except ImportError as e:
    print(f"Error importing Django: {e}")
    print("=" * 60)
    print("DJANGO INSTALLATION REQUIRED")
    print("=" * 60)
    print("Django is not installed on this server.")
    print("To fix this issue, run the following commands on your server:")
    print("")
    print("1. Navigate to your project directory:")
    print(f"   cd {project_dir}")
    print("")
    print("2. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("")
    print("3. If using a virtual environment, activate it first:")
    print("   source venv/bin/activate  # For Linux/Unix")
    print("   # or")
    print("   venv\\Scripts\\activate     # For Windows")
    print("")
    print("4. Then install dependencies:")
    print("   pip install -r requirements.txt")
    print("")
    print(f"Current Python path: {sys.path}")
    print("=" * 60)
    raise

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitbio.settings")

# Get the WSGI application
application = get_wsgi_application()

# Optional: Add any additional configuration here
# For example, you might want to set up logging or other middleware

# Configure Passenger logging using Django's logging configuration
import logging

# Ensure logs directory exists
log_dir = os.path.join(project_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

# Get the passenger logger (will use Django's logging configuration)
passenger_logger = logging.getLogger("passenger")
passenger_logger.info("Passenger WSGI application started")

if __name__ == "__main__":
    # This allows the file to be run directly for testing
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
