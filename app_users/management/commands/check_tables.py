from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Check what tables exist in the database and clean up leftover tables'

    def handle(self, *args, **options):
        self.stdout.write('Checking database tables...')
        
        try:
            with connection.cursor() as cursor:
                # Show all tables
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                if tables:
                    self.stdout.write('Existing tables:')
                    for table in tables:
                        self.stdout.write(f'  - {table[0]}')
                    
                    # Check if admin_log table exists
                    admin_log_exists = any('django_admin_log' in table[0] for table in tables)
                    if admin_log_exists:
                        self.stdout.write('\nFound django_admin_log table. Dropping it...')
                        cursor.execute("DROP TABLE IF EXISTS django_admin_log")
                        self.stdout.write('✓ Dropped django_admin_log table')
                    
                    # Check for other problematic tables
                    problematic_tables = ['django_admin_log', 'django_content_type', 'django_migrations']
                    for table_name in problematic_tables:
                        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                        if cursor.fetchone():
                            self.stdout.write(f'Found {table_name} table. Dropping it...')
                            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                            self.stdout.write(f'✓ Dropped {table_name} table')
                    
                    self.stdout.write('\nDatabase cleaned up. Now try running migrations again.')
                else:
                    self.stdout.write('No tables found in database.')
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error checking tables: {e}'))
