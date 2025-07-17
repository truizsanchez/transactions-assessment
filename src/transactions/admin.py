from django.contrib import admin

from transactions.models import Account, Transaction

admin.site.register(Account)
admin.site.register(Transaction)