from django.db import models

from transactions.models.account import Account
from transactions.models.mixins import AuditModel


class Transaction(AuditModel):
    class TransactionType(models.TextChoices):
        DEPOSIT = 'deposit', 'Deposit'
        WITHDRAW = 'withdraw', 'Withdraw'

    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="transactions")
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Transaction #{self.pk}: {self.transaction_type} of {self.amount} on {self.created_at}"

    class Meta:
        ordering = ['-created_at']
