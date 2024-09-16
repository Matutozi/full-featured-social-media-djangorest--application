from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializers
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from .models import User
import jwt, datetime

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class LoginView(APIView):
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("User not found")
        
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect Password")
        
        payload = {
            "id": str(user.id),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            "iat": datetime.datetime.utcnow()
        }

        
        token = jwt.encode(payload, "secret", algorithm="HS256")

        

        response_data = {
            "status_code": status.HTTP_200_OK,
            "jwt": token,
             "data": {
                 "access_token": token
             }

        }
        return Response(response_data)
    
    

class UserView(APIView):
    def get(self, request):
        auth_head = request.headers.get("Authorization")

        if not auth_head or not auth_head.startswith("Bearer "):
            raise AuthenticationFailed("Unauthenticated")
        
        token = auth_head.split(" ")[1]

        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        
        user = User.objects.get(id=payload["id"])
        serializer = UserSerializers(user)

        response =  Response({
            "status_code": status.HTTP_200_OK,
            "message": "User details fetched successfully.",
            "data": serializer.data
            })
        
        return response
    

class LogoutView(APIView):
    def post(self, request):
        response_data = {
            "status_code": status.HTTP_200_OK,
            "message": "Logout Successful.",
            "data": {}
        }
        return Response(response_data)