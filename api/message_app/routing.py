from django.urls import re_path
from . import consumers

websocket_urlpatterns = [

    re_path(r'ws/chat/(?P<user_id>\d+)/$', consumers.ChatConsumer.as_asgi(), name='user_chat'),
    re_path(r'ws/group/(?P<group_id>\d+)/$', consumers.ChatConsumer.as_asgi(), name='group_chat'),
]
