from django.db import models
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_messages"
    )
    text = models.TextField()
    attachment = models.FileField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"


class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length=255, unique=True)
    members = models.ManyToManyField(User, related_name="group_members")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.group_name
    
class GroupMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="group_messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_message_sender")
    text = models.TextField()
    attachment = models.FileField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
    
    def __str__(self):
        return f"{self.sender} in {self.group.group_name}: {self.text[:20]}"