import json

from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse

from transactions.models.account import Account
from transactions.models.transaction import Transaction


class WithdrawViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="testpass")
        self.token = Token.objects.create(user=self.user)
        self.account = Account.objects.create(user=self.user, balance=100)

        self.url = reverse("withdraw")

    def test_authenticated_user_can_withdraw(self):
        payload = {
            "amount": 40.00
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("60.00"))
        self.assertEqual(Transaction.objects.count(), 1)
        transaction = Transaction.objects.first()
        self.assertEqual(transaction.transaction_type, Transaction.TransactionType.WITHDRAW)
        self.assertEqual(transaction.amount, Decimal("40"))

    def test_unauthenticated_user_cannot_withdraw(self):
        payload = {
            "amount": 40.00
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_withdraw_more_than_balance_returns_400(self):
        payload = {
            "amount": 150.00  # more than available
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())
        self.assertIn("insufficient", response.json()["error"].lower())

    def test_invalid_amount_returns_400(self):
        payload = {
            "amount": -5.00
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", response.json())

    def test_zero_amount_returns_400(self):
        payload = {
            "amount": 0
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", response.json())

    def test_missing_amount_returns_400(self):
        payload = {}
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", response.json())

    def test_invalid_format_amount_returns_400(self):
        payload = {
            "amount": "nan"
        }
        response = self.client.post(
            self.url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("amount", response.json())
