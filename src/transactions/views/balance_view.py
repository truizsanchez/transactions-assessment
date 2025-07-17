from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from transactions.serializers import BalanceSerializer


class BalanceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=BalanceSerializer,
                description="Current balance of the authenticated user's account."
            )
        },
        description="Retrieve the current balance of the authenticated user's account.",
        examples=[
            OpenApiExample(
                'Successful balance response',
                value={"balance": "420.75"},
                response_only=True
            )
        ]
    )
    def get(self, request):
        account = request.user.account
        serializer = BalanceSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)
