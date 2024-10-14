from django.db import models
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()


class Notification(models.Model):
    NOTIFICATION_TYPE = [
        ("message", "Message Notification"),
        ("post", "Post notification"),
        ("follow", "follow notification"),
        ("unfollow", "unfollow notification"),
        ("general", "General Notification"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[("read", "Read"), ("unread", "Unread")],
        default="unread",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    type = models.CharField(max_length=25, choices=NOTIFICATION_TYPE, default="general")

    def __str__(self):
        return f"Notification for {self.user.username}"


class NotificationSetting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    enable = models.BooleanField(default=False)
    keywords = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Settings for {self.user.username}"
