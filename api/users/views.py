from django.shortcuts import render
from rest_framework.generics import GenericAPIView, UpdateAPIView
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .serializers import (
    UserSerializers,
    CreateUserSerializer,
    UserUpdateSerializer,
    ProfilePicsSerializer,
    CoverPhotosSerializer,
    LoginSerializer,
    FollowSerializer,
    BanUnbanSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .models import User, Follow
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from .models import ProfilePic, CoverPhoto
from django.views.decorators.csrf import csrf_exempt
from response import BaseResponseView
from rest_framework.exceptions import NotFound
from .permissions import IsAdminorStaff
from response import BaseResponseView

JWT_SECRET = settings.SECRET_KEY


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class RegisterView(APIView, BaseResponseView):
    """Method to register a New User"""

    serializer_class = CreateUserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.generate_response(
            status.HTTP_201_CREATED, "User Created Successfully", serializer.data
        )


class LoginView(GenericAPIView):
    """Method to login a user"""

    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, email=email, password=password)

        if user is not None:
            token = get_tokens_for_user(user)["access"]
            refresh_token = get_tokens_for_user(user)["refresh"]

            # print(refresh_token)
            user_data = UserSerializers(user).data

            response_data = {
                "status_code": status.HTTP_200_OK,
                "message": "Authentication successful",
                "data": {
                    "access_token": token,
                    "refresh_token": refresh_token,
                    "user": user_data,
                },
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
    """Method to get user details"""

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializers

    def get(self, request):
        # print(request)
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


class LogoutView(APIView, BaseResponseView):
    """Method to logout a user"""

    permission_classes = [IsAuthenticated]
    serializer_class = None

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            access_token = request.headers.get("Authorization").split()[1]

            if not refresh_token:
                raise AuthenticationFailed("Refresh Token not provided")

            token = RefreshToken(refresh_token)
            token.blacklist()

            return self.generate_response(status.HTTP_200_OK, "Logout Successful")

        except AuthenticationFailed:
            return self.generate_response(
                status.HTTP_400_BAD_REQUEST, "Bad request or token invalid"
            )


class UserProfile(APIView, BaseResponseView):
    """
    Retrieve, update, or delete a user profile.
    """

    serializer_class = UserSerializers
    update_serializer_class = UserUpdateSerializer

    def get_object(self, pk):
        """method to get the id from the route"""

        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("User Not Found")

    def get(self, request, pk, format=None):
        """Retrieve a user profile"""

        user = self.get_object(pk)
        serializer = self.serializer_class(user)
        return self.generate_response(
            status.HTTP_200_OK, "Message Sent", serializer.data
        )

    def get_operation_id(self):
        return "get_user_profile"

    def patch(self, request, pk, format=None):
        """Update user profile"""

        user = self.get_object(pk)
        serializer = self.update_serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.generate_response(
                status.HTTP_200_OK, "User successfully updated", serializer.data
            )

        return self.generate_response(
            status.HTTP_400_BAD_REQUEST, "Failed to update user", serializer.errors
        )

    def delete(self, request, pk, format=None):
        """Delete a user profile"""

        user = self.get_object(pk)
        user.delete()
        return self.generate_response(
            status.HTTP_204_NO_CONTENT, "User successfully deleted"
        )


class ProfilePicsCreation(APIView):
    """Nethod to add profile photo"""

    permission_classes = [IsAuthenticated]
    serializer_class = ProfilePicsSerializer

    def post(self, request, *args, **kwargs):
        """Method to create a cover photo"""
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
        """Method to get cover photo"""
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
    """Method to add a cover photo"""

    permission_classes = [IsAuthenticated]
    serializer_class = CoverPhotosSerializer

    def post(self, request, *args, **kwargs):
        """Method to create a cover photo"""
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
        """Method to get cover photo"""
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


class FollowViewSet(APIView, BaseResponseView):
    """View for follow and unfollow functionality"""

    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def post(self, request, user_id):
        """Method to follow a user"""
        if user_id == request.user.id:
            return Response(
                {
                    "status_code": status.HTTP_406_NOT_ACCEPTABLE,
                    "message": "Cannot follow yourself",
                },
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        try:
            user_to_follow = User.objects.get(id=user_id)
            if Follow.objects.filter(
                follower=request.user, followed=user_to_follow
            ).exists():
                return self.generate_response(
                    status.HTTP_400_BAD_REQUEST, "You alreday follow this user"
                )

            follow = Follow.objects.create(
                follower=request.user, followed=User.objects.get(id=user_id)
            )
            serializer = self.serializer_class(follow)
            response_data = {
                "status_code": status.HTTP_201_CREATED,
                "message": f"{request.user.username} followed successfully",
                "data": serializer.data,
            }
            # add the notification here
            return Response(response_data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(
                {
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "User with ID {} not found".format(user_id),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, user_id):
        """Method to unfollow a user"""

        follow = Follow.objects.filter(
            follower=request.user, followed=User.objects.get(id=user_id)
        ).first()
        if follow:
            follow.delete()
            return Response(
                {
                    "status_code": status.HTTP_204_NO_CONTENT,
                    "message": "User successfully unfollowed",
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return Response(
                {
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "message": "You are not following this user",
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class BanUserView(UpdateAPIView, BaseResponseView):
    """Class that bans a specific user"""

    queryset = User.objects.all()
    serializer_class = BanUnbanSerializer
    permission_classes = [IsAuthenticated, IsAdminorStaff]

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        data = {"ban": True}
        serializer = self.get_serializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.generate_response(
                status.HTTP_202_ACCEPTED, "User ban Successful"
            )
        return self.generate_response(
            status.HTTP_400_BAD_REQUEST, "User Ban not successful", serializer.errors
        )


class UnBanUserView(UpdateAPIView, BaseResponseView):
    """Class that unbans a specific user"""

    queryset = User.objects.all()
    serializer_class = BanUnbanSerializer
    permission_classes = [IsAuthenticated, IsAdminorStaff]

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        data = {"ban": False}
        serializer = self.get_serializer(user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.generate_response(
                status.HTTP_202_ACCEPTED, "User UnBan Successful"
            )
        return self.generate_response(
            status.HTTP_400_BAD_REQUEST, "User Unban not successful", serializer.errors
        )
