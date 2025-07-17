# views/logout_view.py
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView


# Logs out the authenticated user by deleting their token.
# This view is added to support OpenAPI documentation.
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        description="Logs out the current user by deleting their authentication token.",
        responses={
            200: OpenApiResponse(description="Successfully logged out."),
        }
    )
    def post(self, request):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
        except Token.DoesNotExist:
            pass  # Token may already be deleted or never created

        return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
