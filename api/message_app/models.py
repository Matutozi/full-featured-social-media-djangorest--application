from django.db import models
import uuid
from users.models import User


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.TextField()
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"
