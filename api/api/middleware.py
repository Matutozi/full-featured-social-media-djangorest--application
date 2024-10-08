from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from django.utils.deprecation import MiddlewareMixin
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
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
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        user = User.objects.get(id=user_id)
        return user
    
    except (User.DoesNotExist, jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return AnonymousUser()


class QueryAuthMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up user from query string (you should also do things like
        # checking if it is a valid user ID, or if scope["user"] is already
        # populated).
        print("running")
        headers = scope.get("headers")
        authorization_header = headers.get(b"authorization")
        if authorization_header:
            authorization_header = authorization_header.decode("utf-8")

        if authorization_header and authorization_header.startswith("Bearer "):
            token = authorization_header.split(" ")[1]
            scope["user"] = await get_user(token)
        else:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)
