from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializers, CreateUserSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework import status
from .models import User
import jwt, datetime
from django.conf import settings

JWT_SECRET = settings.SECRET_KEY


class RegisterView(APIView):
    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            raise AuthenticationFailed("Email and Password required")

        user = User.objects.filter(email=email).first()

        """  FOR DEBUG
        print(user)
        print(user.check_password(password))
        print(password)
        print(request.data)

        """
        if user is None:
            raise AuthenticationFailed("User not found")

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect Password")

        payload = {
            "id": str(user.id),
            "email": user.email,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            "iat": datetime.datetime.utcnow(),
        }

        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

        response_data = {
            "status_code": status.HTTP_200_OK,
            "jwt": token,
            "data": {"access_token": token},
        }
        return Response(response_data)




class LogoutView(APIView):
    def post(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"detail": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        token = auth_header.split(" ")[1]

        try:
            refresh_token = RefreshToken(token)
            refresh_token.blacklist()
        except TokenError:
            raise AuthenticationFailed("Invalid Token")
        

        response_data = {
            "status_code": status.HTTP_200_OK,
            "message": "Logout Successful.",
            "data": {},
        }
        return Response(response_data)


class UserView(APIView):
    def get(self, request):
        print("USER VIEW")
        auth_head = request.headers.get("Authorization")

        #print(auth_head)

        if not auth_head or not auth_head.startswith("Bearer "):
            raise AuthenticationFailed("Unauthenticated-  No token provided")

        token = auth_head.split(" ")[1]
        print(token)

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithm="HS256")
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated- Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        print(payload)

        user_data = {
            "id": payload["id"],
            "email": payload["email"],

        }

        response = Response(
            {
                "status_code": status.HTTP_200_OK,
                "message": "User details fetched successfully.",
                "data": user_data
            }
        )

        return response