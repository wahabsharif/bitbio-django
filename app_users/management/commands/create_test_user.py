from django.core.management.base import BaseCommand
from app_users.models import User


class Command(BaseCommand):
    help = "Create a test user with approved status for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            default="test@example.com",
            help="Email for the test user",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="testpass123",
            help="Password for the test user",
        )

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            user.status = "approved"
            user.is_active = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f"User {email} already exists and has been approved")
            )
        else:
            # Create new user
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name="Test",
                last_name="User",
                job_title="Tester",
                status="approved",
                is_active=True,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created approved user {email}")
            )

        self.stdout.write(f"Email: {email}")
        self.stdout.write(f"Password: {password}")
        self.stdout.write(f"Status: {user.status}")
        self.stdout.write(
            "You can now use these credentials to test the calculator login."
        )
