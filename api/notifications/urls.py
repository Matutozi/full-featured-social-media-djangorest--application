from django.urls import path
from .views import stream_notifications

urlpatterns = [
    path("stream/<uuid:user_id>/", stream_notifications, name="stream-notifications"),
]
