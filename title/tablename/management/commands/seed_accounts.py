from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tablename.models import UserProfile, Employee


PREDEFINED_ACCOUNTS = [
    {
        'username': 'admin',
        'password': 'Admin@1234',
        'full_name': 'System Administrator',
        'role': 'admin',
        'position': 'Administrator',
        'department': 'Management',
    },
    {
        'username': 'hr_manager',
        'password': 'HR@1234',
        'full_name': 'HR Manager',
        'role': 'hr',
        'position': 'HR Manager',
        'department': 'Human Resources',
    },
]


class Command(BaseCommand):
    help = 'Creates predefined Admin and HR accounts'

    def handle(self, *args, **kwargs):
        for account in PREDEFINED_ACCOUNTS:
            if User.objects.filter(username=account['username']).exists():
                self.stdout.write(f"  Account '{account['username']}' already exists — skipped.")
                continue

            name_parts = account['full_name'].split(' ', 1)
            user = User.objects.create_user(
                username=account['username'],
                password=account['password'],
                first_name=name_parts[0],
                last_name=name_parts[1] if len(name_parts) > 1 else '',
            )
            UserProfile.objects.create(user=user, role=account['role'])
            Employee.objects.create(
                employee_id=account['username'].upper(),
                user=user,
                first_name=name_parts[0],
                last_name=name_parts[1] if len(name_parts) > 1 else '',
                name=account['full_name'],
                role=account['role'],
                role_locked=True,
                identity_verified=True,
                position=account['position'],
                department=account['department'],
                status='Active',
            )
            self.stdout.write(self.style.SUCCESS(
                f"  Created '{account['username']}' ({account['role']}) — password: {account['password']}"
            ))

        self.stdout.write(self.style.SUCCESS('\nDone! Predefined accounts are ready.'))
