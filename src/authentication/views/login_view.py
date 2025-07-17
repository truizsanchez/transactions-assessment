from drf_spectacular.utils import OpenApiExample, extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken


# This subclass exists solely to provide OpenAPI documentation via drf-spectacular.
# It does not modify the logic of ObtainAuthToken in any way.
class LoginView(ObtainAuthToken):

    @extend_schema(
        description="Obtain an authentication token by providing username and password.",
        request=inline_serializer(
        name="AuthTokenRequest",
        fields={
            'username': serializers.CharField(),
            'password': serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)
        }
    ),
        responses={
            200: inline_serializer(
                name='TokenResponse',
                fields={'token': serializers.CharField()}
            )
        },
        examples=[
            OpenApiExample(
                'Login example',
                summary='Basic auth token request',
                description='Provide username and password to receive an authentication token.',
                value={
                    "username": "user1",
                    "password": "testpass"
                },
                request_only=True
            )
        ]
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response
