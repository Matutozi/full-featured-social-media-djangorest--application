from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializers, CreateUserSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from .models import User
import jwt, datetime


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

        if password is None:
            raise AuthenticationFailed("Password Required")

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
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            "iat": datetime.datetime.utcnow(),
        }

        token = jwt.encode(payload, "secret", algorithm="HS256")
        print(token)
        response_data = {
            "status_code": status.HTTP_200_OK,
            "jwt": token,
            "data": {"access_token": token},
        }
        return Response(response_data)




class LogoutView(APIView):
    def post(self, request):
        response_data = {
            "status_code": status.HTTP_200_OK,
            "message": "Logout Successful.",
            "data": {},
        }
        return Response(response_data)

class UserView(APIView):
    def get(self, request):
        print("Hell")
        auth_head = request.headers.get("Authorization")

        #print(auth_head)

        if not auth_head or not auth_head.startswith("Bearer "):
            raise AuthenticationFailed("Unauthenticated")

        token = auth_head.split(" ")[1]
        print(token)

        try:
            payload = jwt.decode(token, "secret", algorithm="HS256")
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")

        print(payload)

        user = User.objects.get(id=payload["id"])
        serializer = UserSerializers(user)

        response = Response(
            {
                "status_code": status.HTTP_200_OK,
                "message": "User details fetched successfully.",
                "data": serializer.data,
            }
        )

        return response