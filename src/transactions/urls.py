from django.urls import path

from transactions.views.balance_view import BalanceView
from transactions.views.deposit_view import DepositView
from transactions.views.withdraw_view import WithdrawView

urlpatterns = [
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('balance/', BalanceView.as_view(), name='balance'),
]
