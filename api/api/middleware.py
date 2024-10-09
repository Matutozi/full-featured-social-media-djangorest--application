from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from django.utils.deprecation import MiddlewareMixin
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
User = get_user_model()


class SyncQueryAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        authorization_header = request.META.get("HTTP_AUTHORIZATION")
        token = None

        if authorization_header and authorization_header.startswith("Bearer "):
            token = authorization_header.split(" ")[1]

        if token:
            try:
                token_obj = Token.objects.get(key=token)
                request.user = token_obj.user
            except Token.DoesNotExist:
                request.user = AnonymousUser()
        else:
            request.user = AnonymousUser()


@database_sync_to_async
def get_user(token):
    try:
        #payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        accesstoken = AccessToken(token)
        user_id = accesstoken.get("user_id")
        user = User.objects.get(id=user_id)
        print(f"User found: {user.username}")
        return user
    except User.DoesNotExist as e:
        print("User does not exist:", str(e))
        return AnonymousUser()
    except jwt.ExpiredSignatureError as e:
        print("Token has expired:", str(e))
        return AnonymousUser()
    except jwt.InvalidTokenError as e:
        print("Invalid token:", str(e)) 
        return AnonymousUser()


class QueryAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        print("middleware is running")
        headers = scope.get("headers")
        authorization_header = None

        # Iterate through headers to find the authorization header
        for name, value in headers:
            if name == b"authorization":
                authorization_header = value.decode("utf-8")
                break

        if authorization_header and authorization_header.startswith("Bearer "):
            token = authorization_header.split(" ")[1]
            print("Token received:", token)
            #print("I reached here")
            scope["user"] = await get_user(token)
            print("User retrieval ", scope["user"])
        else:
            scope["user"] = AnonymousUser()
            print("No authorization header found, user set to Anonymous")

        return await self.app(scope, receive, send)
