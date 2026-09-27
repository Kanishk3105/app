"""Authentication views: registration and JWT login."""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.models import User
from apps.accounts.serializers import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ - create a new account."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "User registered successfully.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """POST /api/auth/login/ - exchange credentials for a JWT pair."""

    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """POST /api/auth/logout/ - blacklist/ignore the presented refresh token."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


class MeView(APIView):
    """GET /api/auth/me/ - return the currently authenticated user."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


class TokenRefreshViewWithPayload(TokenRefreshView):
    """POST /api/auth/token/refresh/ - rotate the access token."""

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.data = {"message": "Token refreshed.", **response.data}
        return response


__all__ = [
    "RegisterView",
    "LoginView",
    "LogoutView",
    "MeView",
    "TokenRefreshViewWithPayload",
]
