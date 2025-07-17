from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from transactions.models import Account
from transactions.serializers import BalanceSerializer


class BalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        account: Account = request.user.account
        serializer = BalanceSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)
