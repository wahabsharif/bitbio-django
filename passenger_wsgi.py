#!/usr/bin/env python3
"""
Passenger WSGI file for BitBio Django application.

This file is used by Passenger to serve the Django application.
Make sure to adjust the paths according to your server setup.
"""

import os
import sys
import django
from django.core.wsgi import get_wsgi_application

# Add the project directory to the Python path
# Adjust this path to match your server's directory structure
project_dir = os.path.dirname(os.path.abspath(__file__))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitbio.settings")

# Initialize Django
django.setup()

# Get the WSGI application
application = get_wsgi_application()

# Optional: Add any additional configuration here
# For example, you might want to set up logging or other middleware

if __name__ == "__main__":
    # This allows the file to be run directly for testing
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
