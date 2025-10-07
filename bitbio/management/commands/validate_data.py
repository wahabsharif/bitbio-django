"""
Management command to validate and manage data files
Usage: python manage.py validate_data
       python manage.py validate_data --clear-cache
"""

import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from bitbio.utils.data_loader import clear_data_cache, get_navigation_data


class Command(BaseCommand):
    help = "Validate data files and manage data cache"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear-cache",
            action="store_true",
            help="Clear the data cache",
        )
        parser.add_argument(
            "--list",
            action="store_true",
            help="List all data files",
        )

    def handle(self, *args, **options):
        data_dir = Path(settings.BASE_DIR) / "bitbio" / "data"

        if options["clear_cache"]:
            clear_data_cache()
            self.stdout.write(self.style.SUCCESS("✓ Data cache cleared"))
            return

        if options["list"]:
            self.list_data_files(data_dir)
            return

        # Default: validate all JSON files
        self.stdout.write(self.style.MIGRATE_HEADING("Validating data files..."))

        json_files = list(data_dir.glob("*.json"))

        if not json_files:
            self.stdout.write(
                self.style.WARNING("⚠ No JSON files found in data directory")
            )
            return

        valid_count = 0
        invalid_count = 0

        for json_file in json_files:
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Basic validation
                if isinstance(data, dict):
                    keys = len(data.keys())
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ {json_file.name} - Valid ({keys} top-level keys)"
                        )
                    )
                elif isinstance(data, list):
                    items = len(data)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ {json_file.name} - Valid ({items} items)"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠ {json_file.name} - Valid JSON but unexpected type"
                        )
                    )

                valid_count += 1

            except json.JSONDecodeError as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ {json_file.name} - Invalid JSON: {e}")
                )
                invalid_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ {json_file.name} - Error: {e}"))
                invalid_count += 1

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Summary:"))
        self.stdout.write(f"Total files: {len(json_files)}")
        self.stdout.write(self.style.SUCCESS(f"Valid: {valid_count}"))
        if invalid_count > 0:
            self.stdout.write(self.style.ERROR(f"Invalid: {invalid_count}"))

        # Test loading navigation
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Testing navigation data..."))
        try:
            nav_data = get_navigation_data()
            if nav_data:
                menu_count = len(nav_data.get("main_menu", []))
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Navigation loaded successfully ({menu_count} menu items)"
                    )
                )
            else:
                self.stdout.write(self.style.WARNING("⚠ Navigation data is empty"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Failed to load navigation: {e}"))

    def list_data_files(self, data_dir):
        """List all data files"""
        self.stdout.write(self.style.MIGRATE_HEADING("Data files:"))

        for file in sorted(data_dir.glob("*")):
            if file.is_file() and not file.name.startswith("."):
                size = file.stat().st_size
                size_kb = size / 1024
                self.stdout.write(f"  • {file.name} ({size_kb:.1f} KB)")
