#!/usr/bin/env python3
"""
Script to install PDF generation dependencies for the bit.bio Django application.
Run this script on the production server to install WeasyPrint and its dependencies.
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Installing {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✓ {description} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {description}: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    print("Installing PDF generation dependencies for bit.bio Django application...")
    print("=" * 60)

    # Check if we're in the right directory
    if not os.path.exists("manage.py"):
        print("Error: Please run this script from the Django project root directory")
        sys.exit(1)

    # Install WeasyPrint
    if not run_command("pip install weasyprint", "WeasyPrint"):
        print(
            "Warning: WeasyPrint installation failed. PDF generation will fall back to HTML."
        )

    # Try to install system dependencies (if on Ubuntu/Debian)
    if os.path.exists("/etc/debian_version"):
        print("\nInstalling system dependencies for WeasyPrint...")
        system_deps = [
            "apt-get update",
            "apt-get install -y python3-dev python3-pip python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0",
        ]

        for dep in system_deps:
            if not run_command(f"sudo {dep}", f"System dependency: {dep}"):
                print(f"Warning: Failed to install system dependency: {dep}")

    print("\n" + "=" * 60)
    print("Installation complete!")
    print(
        "\nTo test PDF generation, restart your web server and try the PDF download feature."
    )
    print(
        "If PDF generation still fails, the system will automatically fall back to HTML files."
    )


if __name__ == "__main__":
    main()
