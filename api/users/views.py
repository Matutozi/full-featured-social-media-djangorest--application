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

        response = Response()

        response.set_cookie(key="jwt", value=token, httponly=True)

        response.data = {
                        "jwt": token

        }
        return response
    

class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get("jwt")


        if not token:
            raise AuthenticationFailed("Unauthenticated")
        
        try:
            payload = jwt.decode(token, "secret", algorithms=["HS256"])

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated")
        
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
        response = Response()
        response.delete_cookie("jwt")
        response.data = {
            "status_code": status.HTTP_200_OK,
            "message": "Logout Successful.",
            "data": {}
        }
        return response