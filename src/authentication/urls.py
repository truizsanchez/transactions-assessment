from django.urls import path

from authentication.views.login_view import LoginView
from authentication.views.logout_view import LogoutView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]