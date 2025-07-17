from django.contrib.auth.models import User
from django.db import models

from transactions.models.mixins import AuditModel


class Account(AuditModel):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Account #{self.pk} ({self.user.username})"
