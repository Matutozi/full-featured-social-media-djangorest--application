from .models import Notification


def send_notification(user, message, notification_type="general"):
    """Utility to create and send a notification."""
    Notification.objects.create(user=user, message=message, type=notification_type)
