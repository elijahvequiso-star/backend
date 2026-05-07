from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from tablename.models import UserProfile


class Command(BaseCommand):
    help = "Creates an HR user with Django staff access and an app role of 'hr'."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True, help="Username for the HR account.")
        parser.add_argument("--password", required=True, help="Password for the HR account.")
        parser.add_argument("--full-name", default="", help="Full name for the HR account.")
        parser.add_argument("--email", default="", help="Email address for the HR account.")

    def handle(self, *args, **options):
        username = options["username"].strip()
        password = options["password"]
        full_name = options["full_name"].strip()
        email = options["email"].strip()

        if User.objects.filter(username=username).exists():
            raise CommandError(f"User '{username}' already exists.")

        name_parts = full_name.split(" ", 1) if full_name else ["", ""]
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
            is_superuser=False,
        )

        UserProfile.objects.get_or_create(user=user, defaults={"role": "hr"})

        self.stdout.write(self.style.SUCCESS(f"Created HR user '{username}' successfully."))
