from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from rest_framework.authtoken.models import Token

from transactions.models.account import Account


class Command(BaseCommand):
    help = "Populates the database with test data (user, token, account)"

    def handle(self, *args, **options):
        username = "user1"
        password = "testpass"

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"User '{username}' already exists."))
            return

        user = User.objects.create_user(username=username, password=password)
        token = Token.objects.create(user=user)
        account = Account.objects.create(user=user, balance=100)

        self.stdout.write(self.style.SUCCESS(f"User {username} created with password {password} "))
        self.stdout.write(self.style.SUCCESS(f"Token: {token.key}"))
        self.stdout.write(self.style.SUCCESS(f"Account created with balance: {account.balance}"))
