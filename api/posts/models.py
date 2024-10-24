from django.db import models
import uuid
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    """
    Model representing a social media post.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(null=True)
    image = models.ImageField(null=True, blank=True)
    video = models.FileField(null=True, blank=True)
    tagged_users = models.ManyToManyField(
        User, related_name="tagged_in_posts", blank=True
    )
    hashtags = models.ManyToManyField("Hashtag", related_name="hashing_posts", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Post by {self.user.username}"


class PostComment(models.Model):
    """
    Model representing a comment on a post.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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

    REACTION_CHOICES = [
        ("like", "Like"),
        ("love", "Love"),
        ("laugh", "Laugh"),
        ("sad", "Sad"),
        ("angry", "Angry"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(
        max_length=10, choices=REACTION_CHOICES, default="like"
    )
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
