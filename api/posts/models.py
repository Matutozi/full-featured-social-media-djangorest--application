from django.db import models
import uuid
# Create your models here.
from users.models import User

class Post(models.Model):
    """
    Model representing a social media post.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(null=True)
    image = models.URLField(null=True, blank=True)
    video = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Post by {self.user.username}"
    

class PostComment(models.Model):
    """
    Model representing a comment on a post.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment on {self.post} by {self.post.user.username}"

        
class PostReaction(models.Model):
    """
    Model representing a reaction (like, etc.) on a post.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reaction by {self.user.username} on {self.post}"
    

class Hashtag(models.Model):
    """
    Model representing a hashtag used in posts.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.CharField(max_length=100, unique=True)
    usage = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.tag