from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .serializers import (
    UserSerializers,
    CreateUserSerializer,
    UserUpdateSerializer,
    ProfilePicsSerializer,
    CoverPhotosSerializer,
    LoginSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import Http404
from rest_framework import status
from .models import User
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from .models import ProfilePic, CoverPhoto

JWT_SECRET = settings.SECRET_KEY


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class RegisterView(APIView):
    serializer_class = CreateUserSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, email=email, password=password)

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

class GetUserDetail(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializers

    def get(self, request):
        #print(request)
        user = request.user

        serializer = self.serializer_class(user)

        response = Response(
            {
                "status_code": status.HTTP_200_OK,
                "message": "User details fetched successfully.",
                "data": serializer.data,
            }
        )

        return response

    def get_operation_id(self):
        return "get_user_detail"
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # refresh_token = request.data.get("refresh")
            access_token = request.headers.get("Authorization").split()[1]

            print(access_token)

            token = RefreshToken(access_token)
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
    serializer_class = UserSerializers
    update_serializer_class = UserUpdateSerializer
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """Retrieve a user profile"""

        user = self.get_object(pk)
        serializer = self.serializer_class(user)
        response_data = {
            "status_code": status.HTTP_200_OK,
            "message": "User succedfully retrieved",
            "data": serializer.data,
        }

        return Response(response_data)

    def get_operation_id(self):
        return "get_user_profile"
    
    def patch(self, request, pk, format=None):
        """Update user profile"""

        user = self.get_object(pk)
        serializer = self.update_serializer_class(user, data=request.data)
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


class ProfilePicsCreation(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfilePicsSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Profile picture uploaded successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Failed to upload profile picture.",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get(self, request):
        qs = ProfilePic.objects.all()
        if qs.exists():
            qs_serializer = self.serializer_class(qs, many=True)
            return Response(
                {
                    "status_code": status.HTTP_200_OK,
                    "message": "Profile pictures retrieved successfully.",
                    "data": qs_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "No profile pictures found.",
                    "data": [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class CoverPhotoCreation(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CoverPhotosSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                {
                    "status_code": status.HTTP_201_CREATED,
                    "message": "Cover Photo uploaded successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Failed to upload Cover Photo.",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get(self, request):
        qs = CoverPhoto.objects.all()
        if qs.exists():
            qs_serializer = self.serializer_class(qs, many=True)
            return Response(
                {
                    "status_code": status.HTTP_200_OK,
                    "message": "Cover Photo retrieved successfully.",
                    "data": qs_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "NO Photo found.",
                    "data": [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )
