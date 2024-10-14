"""Script that handles all operations concerned with Post model"""

from .models import Post, PostComment, PostReaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from notifications.views import notification_event
from notifications.utils import send_notification


@receiver(post_save, sender=Post)
def post_create_notification(sender, instance, created, **kwargs):
    """Method that handles the notification for new post creation"""
    if created:
        action = f"New post created by {instance.user.username}"
        send_notification(instance.user, action, notification_type="post")
        notification_event.set()


@receiver(post_save, sender=Post)
def post_update_notification(sender, instance, created, **kwargs):
    if not created:
        action = f"Post updated by {instance.user.username}"
        send_notification(instance.user, action, notification_type="post")
        notification_event.set()


@receiver(post_delete, sender=Post)
def post_delete_notification(sender, instance, **kwargs):
    """Method that handles notification for deletion of post"""
    action = f"Post: {instance.id}  was deleted by {instance.user.username}"
    send_notification(instance.user, action, notification_type="post")
    notification_event.set()


@receiver(post_save, sender=PostComment)
def comment_creation_notification(sender, instance, created, **kwargs):
    """Method that handle notifications for new comment creation."""
    if created:
        action = f"{instance.user.username} commented on your post: {instance.comment}"
        send_notification(instance.post.user, action, notification_type="message")
        notification_event.set()


@receiver(post_delete, sender=PostComment)
def comment_deletion_notification(sender, instance, **kwargs):
    """Method that handle notifications for comment deletion."""
    action = (
        f"Comment deleted on your post by {instance.user.username}: {instance.comment}"
    )
    send_notification(instance.post.user, action, notification_type="message")
    notification_event.set()


@receiver(post_save, sender=PostReaction)
def reaction_notification(sender, instance, created, **kwargs):
    """Handle notifications for reactions to a post."""
    if created:
        action = f"{instance.user.username} reacted with '{instance.reaction_type}' to your post."
        send_notification(instance.post.user, action, notification_type="message")
        notification_event.set()


@receiver(post_delete, sender=PostReaction)
def reaction_deletion_notification(sender, instance, **kwargs):
    """Handle notifications for reaction deletion."""
    action = f"{instance.user.username} removed their '{instance.reaction_type}' reaction from your post."
    send_notification(instance.post.user, action, notification_type="message")
    notification_event.set()
