from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
)

from .serializers import TokenObtainPairSerializer


class TokenPairView(BaseTokenObtainPairView):
    serializer_class = TokenObtainPairSerializer
