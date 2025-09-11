from django.core.management.base import BaseCommand
from app_users.domain_management import clear_domain_cache, get_cached_domain_lists
from app_users.models import Domain


class Command(BaseCommand):
    help = "Clear domain cache and display current domain lists"

    def add_arguments(self, parser):
        parser.add_argument(
            "--test-email",
            type=str,
            help="Test email address to check domain validation",
            default="test@gmail.com",
        )

    def handle(self, *args, **options):
        test_email = options["test_email"]

        self.stdout.write("=== Domain Cache Management ===\n")

        # Show current cached data
        self.stdout.write("Current cached domain lists:")
        cached_data = get_cached_domain_lists()
        self.stdout.write(f"  Whitelisted: {len(cached_data['whitelisted'])} domains")
        self.stdout.write(f"  Blocklisted: {len(cached_data['blocklisted'])} domains")

        # Show specific domain status
        from app_users.domain_management import (
            get_email_domain,
            is_blocklisted_domain,
            is_blocklisted_domain_direct,
        )

        domain = get_email_domain(test_email)
        is_blocked = is_blocklisted_domain(test_email)
        is_blocked_direct = is_blocklisted_domain_direct(test_email)
        self.stdout.write(f"  '{domain}' is blocked (cached): {is_blocked}")
        self.stdout.write(f"  '{domain}' is blocked (database): {is_blocked_direct}")

        # Clear cache
        self.stdout.write("\nClearing domain cache...")
        clear_domain_cache()

        # Show database data
        self.stdout.write("\nDatabase domain lists:")
        try:
            domain_obj = Domain.objects.first()
            if domain_obj:
                self.stdout.write(
                    f"  Whitelisted: {len(domain_obj.whitelisted_domains or [])} domains"
                )
                self.stdout.write(
                    f"  Blocklisted: {len(domain_obj.blocklisted_domains or [])} domains"
                )

                # Check if specific domain is in database
                is_in_db_blocklist = domain in (domain_obj.blocklisted_domains or [])
                self.stdout.write(
                    f"  '{domain}' in database blocklist: {is_in_db_blocklist}"
                )
            else:
                self.stdout.write("  No domain object found in database!")
        except Exception as e:
            self.stdout.write(f"  Database error: {e}")

        # Test after cache clear
        self.stdout.write("\nAfter cache clear:")
        new_cached_data = get_cached_domain_lists()
        new_is_blocked = is_blocklisted_domain(test_email)
        new_is_blocked_direct = is_blocklisted_domain_direct(test_email)
        self.stdout.write(
            f"  New cached blocklisted: {len(new_cached_data['blocklisted'])} domains"
        )
        self.stdout.write(f"  '{domain}' is now blocked (cached): {new_is_blocked}")
        self.stdout.write(
            f"  '{domain}' is now blocked (database): {new_is_blocked_direct}"
        )

        # Test form validation
        self.stdout.write(f"\nTesting form validation for {test_email}:")
        from app_users.domain_management import should_block_registration

        should_block = should_block_registration(test_email)
        self.stdout.write(f"  should_block_registration(): {should_block}")

        if should_block:
            self.stdout.write(
                self.style.WARNING(
                    f"WARNING: {test_email} is still being blocked. "
                    "Check database content and remove from blocklisted_domains."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"SUCCESS: {test_email} is no longer blocked.")
            )

        self.stdout.write("\n=== Complete ===")
