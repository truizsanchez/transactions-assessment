from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse

from transactions.models.account import Account


class BalanceViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="testpass")
        self.token = Token.objects.create(user=self.user)
        self.account = Account.objects.create(user=self.user, balance=250.75)

        self.url = reverse("balance")

    def test_authenticated_user_can_view_balance(self):
        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'balance': '250.75'})

    def test_unauthenticated_user_cannot_view_balance(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_balance_can_be_negative(self):
        self.account.balance = -0.01
        self.account.save()

        response = self.client.get(
            self.url,
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {'balance': '-0.01'})
