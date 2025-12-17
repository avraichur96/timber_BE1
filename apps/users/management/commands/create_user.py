from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
import getpass

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a new user with username and password'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the new user')
        parser.add_argument('--email', type=str, help='Email for the new user')
        parser.add_argument('--password', type=str, help='Password for the new user')
        parser.add_argument('--first-name', type=str, help='First name for the new user')
        parser.add_argument('--last-name', type=str, help='Last name for the new user')
        parser.add_argument('--superuser', action='store_true', help='Create as superuser')
        parser.add_argument('--staff', action='store_true', help='Create as staff user')

    def handle(self, *args, **options):
        # Get user input if not provided via arguments
        username = options.get('username') or input('Username: ')
        email = options.get('email') or input('Email: ')
        
        if not username or not email:
            self.stdout.write(self.style.ERROR('Username and email are required'))
            return

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User with username "{username}" already exists'))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'User with email "{email}" already exists'))
            return

        # Get password
        password = options.get('password') or getpass.getpass('Password: ')
        if not password:
            self.stdout.write(self.style.ERROR('Password is required'))
            return

        # Get optional fields
        first_name = options.get('first_name') or input('First name (optional): ') or ''
        last_name = options.get('last_name') or input('Last name (optional): ') or ''

        # Create user
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
        }

        if options.get('superuser'):
            user = User.objects.create_superuser(**user_data)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully'))
        elif options.get('staff'):
            user = User.objects.create_user(**user_data)
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Staff user "{username}" created successfully'))
        else:
            user = User.objects.create_user(**user_data)
            self.stdout.write(self.style.SUCCESS(f'User "{username}" created successfully'))

        # Create auth token
        token, created = Token.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS(f'Auth token: {token.key}'))

        # Display user info
        self.stdout.write('\nUser Details:')
        self.stdout.write(f'  ID: {user.id}')
        self.stdout.write(f'  Username: {user.username}')
        self.stdout.write(f'  Email: {user.email}')
        self.stdout.write(f'  Is Active: {user.is_active}')
        self.stdout.write(f'  Is Staff: {user.is_staff}')
        self.stdout.write(f'  Is Superuser: {user.is_superuser}')
        self.stdout.write(f'  Created: {user.created_at}')
