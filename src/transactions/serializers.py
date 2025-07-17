from decimal import Decimal

from rest_framework import serializers

from transactions.models.account import Account


class TransactionSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
        help_text="Amount to operate."
    )


class BalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['balance']
