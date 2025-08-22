from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Complete database reset - drops all Django tables and starts fresh"

    def handle(self, *args, **options):
        self.stdout.write("Performing complete database reset...")

        try:
            with connection.cursor() as cursor:
                # Get all tables in the database
                cursor.execute("SHOW TABLES")
                all_tables = cursor.fetchall()

                if all_tables:
                    self.stdout.write("Dropping all existing tables:")
                    for table in all_tables:
                        table_name = table[0]
                        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                        self.stdout.write(f"✓ Dropped {table_name}")

                    self.stdout.write("\nAll tables dropped successfully!")
                else:
                    self.stdout.write("No tables found in database.")

                self.stdout.write(self.style.SUCCESS("\nDatabase completely reset!"))
                self.stdout.write("Now you can run: python manage.py migrate")
                self.stdout.write(
                    "This will create all tables in the correct order automatically."
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during complete reset: {e}"))
