from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .serializers import UserSerializers, CreateUserSerializer, UserUpdateSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import Http404
from rest_framework import status
from .models import User
import jwt
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

JWT_SECRET = settings.SECRET_KEY


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class RegisterView(APIView):
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:

            response_data = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Email and Password required",
                "data": {},
            }
            return Response(response_data, status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        # user = User.objects.filter(email=email).first()

        """  FOR DEBUG
        print(user)
        print(user.check_password(password))
        print(password)
        print(request.data)

        """

        if user is not None:
            token = get_tokens_for_user(user)["access"]

            response_data = {
                "status_code": status.HTTP_200_OK,
                "message": "Authentication successful",
                "data": {"access_token": token},
            }
            return Response(response_data, status=status.HTTP_200_OK)

        else:
            response_data = {
                "status_code": status.HTTP_401_UNAUTHORIZED,
                "message": "Invalid credentials",
                "data": {},
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)


class UserView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        print(request)
        user = request.user

        serializer = UserSerializers(user)

        response = Response(
            {
                "status_code": status.HTTP_200_OK,
                "message": "User details fetched successfully.",
                "data": serializer.data,
            }
        )

        return response


class LogoutView(APIView):
    [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")

            token = RefreshToken(refresh_token)
            token.blacklist()

            response_data = {
                "status_code": status.HTTP_200_OK,
                "message": "Logout Successful.",
                "data": {},
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except AuthenticationFailed:
            response_data = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Bad request or token invalid",
                "data": {},
            }
            return Response(response_data)


class UserProfile(APIView):
    """
    Retrieve, update, or delete a user profile.
    """

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """Retrieve a user profile"""

        user = self.get_object(pk)
        serializer = UserSerializers(user)
        response_data = {
            "status_code": status.HTTP_200_OK,
            "message": "User succedfully retrieved",
            "data": serializer.data,
        }

        return Response(response_data)

    def patch(self, request, pk, format=None):
        """Update user profile"""

        user = self.get_object(pk)
        serializer = UserUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                "status_code": status.HTTP_200_OK,
                "message": "User successfully Updated",
                "data": serializer.data,
            }
            return Response(response_data)

        response_data = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "message": "Failed to update user.",
            "data": serializer.errors,
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """Delete a user profile"""

        user = self.get_object(pk)
        user.delete()
        response_data = {
            "status_code": status.HTTP_204_NO_CONTENT,
            "message": "User deleted successfully.",
            "data": {},
        }
        return Response(response_data)
