from django.urls import path

from apps.authentication.adapters.views import TokenPairView

urlpatterns = [
    path("api/v1/auth/token/", TokenPairView.as_view(), name="auth-token"),
]
