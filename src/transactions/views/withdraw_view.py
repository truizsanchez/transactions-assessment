import time

from decimal import Decimal

from django.db import transaction
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from transactions.models import Account
from transactions.models.transaction import Transaction
from transactions.serializers import TransactionSerializer


class WithdrawView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            amount: Decimal = serializer.validated_data['amount']
            account: Account = request.user.account

            if account.balance < amount:
                return Response(
                    {'error': 'Insufficient funds'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            with transaction.atomic():
                time.sleep(0.2)  # Simulación de retardo (¿tal vez para condiciones de carrera?)
                account.balance -= amount
                account.save()
                Transaction.objects.create(
                    account=account,
                    transaction_type=Transaction.TransactionType.WITHDRAW,
                    amount=amount
                )
            return Response(
                {'message': 'Withdrawal successful', 'new_balance': account.balance},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
