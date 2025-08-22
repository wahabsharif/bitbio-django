from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import getpass

User = get_user_model()


class Command(BaseCommand):
    help = "Create a new admin user for BitBio"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email", type=str, help="Email address for the admin user"
        )
        parser.add_argument(
            "--first-name", type=str, help="First name for the admin user"
        )
        parser.add_argument(
            "--last-name", type=str, help="Last name for the admin user"
        )
        parser.add_argument(
            "--job-title", type=str, help="Job title for the admin user"
        )
        parser.add_argument(
            "--password",
            type=str,
            help="Password for the admin user (will prompt if not provided)",
        )
        parser.add_argument(
            "--superuser",
            action="store_true",
            help="Create a superuser instead of a regular admin user",
        )

    def handle(self, *args, **options):
        try:
            # Get email
            email = options["email"]
            if not email:
                email = input("Enter email address: ").strip()

            if not email:
                raise CommandError("Email address is required")

            # Validate email format
            try:
                validate_email(email)
            except ValidationError:
                raise CommandError("Invalid email format")

            # Check if user already exists
            if User.objects.filter(email=email).exists():
                raise CommandError(f"User with email {email} already exists")

            # Get first name
            first_name = options["first_name"]
            if not first_name:
                first_name = input("Enter first name: ").strip()

            if not first_name:
                raise CommandError("First name is required")

            # Get last name
            last_name = options["last_name"]
            if not last_name:
                last_name = input("Enter last name: ").strip()

            if not last_name:
                raise CommandError("Last name is required")

            # Get job title
            job_title = options["job_title"]
            if not job_title:
                job_title = input("Enter job title: ").strip()

            if not job_title:
                raise CommandError("Job title is required")

            # Get password
            password = options["password"]
            if not password:
                password = getpass.getpass("Enter password: ")
                password_confirm = getpass.getpass("Confirm password: ")

                if password != password_confirm:
                    raise CommandError("Passwords do not match")

            if not password:
                raise CommandError("Password is required")

            # Create user
            if options["superuser"]:
                user = User.objects.create_superuser(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    job_title=job_title,
                    status="approved",
                )
                user_type = "superuser"
            else:
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    job_title=job_title,
                    is_staff=True,
                    is_superuser=True,
                    status="approved",
                )
                user_type = "superuser"

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created {user_type}:\n"
                    f"  Email: {user.email}\n"
                    f"  Name: {user.first_name} {user.last_name}\n"
                    f"  Job Title: {user.job_title}\n"
                    f"  Staff Status: {user.is_staff}\n"
                    f"  Superuser Status: {user.is_superuser}\n"
                    f"  Approval Status: {user.status}"
                )
            )

            self.stdout.write(
                self.style.WARNING(
                    "\nYou can now log in to the admin panel at:\n"
                    "  http://localhost:8000/admin/\n"
                    "  or\n"
                    "  http://127.0.0.1:8000/admin/"
                )
            )

        except KeyboardInterrupt:
            self.stdout.write(self.style.ERROR("\nOperation cancelled by user"))
        except Exception as e:
            raise CommandError(f"Error creating admin user: {str(e)}")
