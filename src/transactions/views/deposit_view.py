import logging

from decimal import Decimal

from django.db import transaction
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from transactions.models import Account
from transactions.models.transaction import Transaction
from transactions.serializers import TransactionSerializer

logger = logging.getLogger(__name__)


class DepositView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=TransactionSerializer,
        responses={
            200: OpenApiResponse(
                description="Deposit successful",
                response=None
            ),
            400: OpenApiResponse(
                description="Invalid data",
                response=None
            )
        },
        description="Deposit an amount into the authenticated user's account.",
        examples=[
            OpenApiExample(
                'Valid deposit example',
                value={"amount": "100.00"},
                request_only=True
            ),
            OpenApiExample(
                'Too small amount example',
                value={"amount": "0.00"},
                request_only=True
            )
        ]
    )
    def post(self, request: Request) -> Response:
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            amount: Decimal = serializer.validated_data['amount']
            account: Account = request.user.account

            with transaction.atomic():
                account.balance += amount
                account.save()
                Transaction.objects.create(
                    account=account,
                    transaction_type=Transaction.TransactionType.DEPOSIT,
                    amount=amount
                )
            logger.info(f"User {request.user.username} deposited {amount}. New balance: {account.balance}")
            return Response(
                {'message': 'Deposit successful', 'new_balance': account.balance},
                status=status.HTTP_200_OK
            )
        logger.warning(f"User {request.user.username} failed to deposit. Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
