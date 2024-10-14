import json
from django.http import StreamingHttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from .models import Notification
from threading import Event

notification_event = Event()

def fetch_notifications(user_id: int):
    """Fetch notifications for the given user in real-time."""
    yield f"data: {json.dumps([])}\n\n"

    while True:
        notification_event.wait()  
        notifications = json.dumps(
            list(
                Notification.objects.filter(user_id=user_id).values(
                    "id", "message", "created_at", "status"
                ).order_by('-created_at')[:10],
                cls=DjangoJSONEncoder,
            )
        )
        yield f"data: {notifications}\n\n"
        notification_event.clear()

def stream_notifications(request, user_id):
    """Stream notifications to the client."""
    response = StreamingHttpResponse(fetch_notifications(user_id))
    response["Content-Type"] = "text/event-stream"
    return response
