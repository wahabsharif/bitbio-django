from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = "Create a superuser with email authentication"

    def add_arguments(self, parser):
        parser.add_argument("--email", type=str, help="Superuser email")
        parser.add_argument("--first-name", type=str, help="Superuser first name")
        parser.add_argument("--last-name", type=str, help="Superuser last name")
        parser.add_argument("--job-title", type=str, help="Superuser job title")
        parser.add_argument("--password", type=str, help="Superuser password")

    def handle(self, *args, **options):
        email = options.get("email")
        first_name = options.get("first_name")
        last_name = options.get("last_name")
        job_title = options.get("job_title")
        password = options.get("password")

        if not email:
            email = input("Email: ")
        if not first_name:
            first_name = input("First name: ")
        if not last_name:
            last_name = input("Last name: ")
        if not job_title:
            job_title = input("Job title: ")
        if not password:
            password = input("Password: ")
            password_confirm = input("Password (again): ")
            if password != password_confirm:
                self.stdout.write(self.style.ERROR("Passwords do not match"))
                return

        try:
            with transaction.atomic():
                user = User.objects.create_superuser(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    job_title=job_title,
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Superuser created successfully: {user.email}")
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error creating superuser: {e}"))

