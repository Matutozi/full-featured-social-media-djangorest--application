"""Script that handles all the signal operations concerned with user model"""

from .models import User, ProfilePic, CoverPhoto, Follow
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from notifications.utils import send_notification
from notifications.views import notification_event


@receiver(post_save, sender=User)
def user_register_notification(sender, instance, created, **kwargs):
    """Method that handles the notification for new user creation"""
    if created:
        action = f"New User Created: {instance.username}"
        #print(action)
        send_notification(instance, action, notification_type="general")
        notification_event.set()


@receiver(post_delete, sender=User)
def user_deletion_notification(sender, instance, **kwargs):
    """Method that handles the notification for user deletion"""
    action = f"User deleted: {instance.username}"
    send_notification(instance, action, notification_type="general")
    notification_event.set()


@receiver(post_save, sender=ProfilePic)
def profile_pics_creation_notification(sender, instance, created, **kwargs):
    """Method that handles the notification for profile pics upload"""
    if created:
        user = instance.user
        action = f"Profile Pics Uploaded for User: {instance.user.username}"
        send_notification(user, action, notification_type="general")
        notification_event.set()


@receiver(post_delete, sender=ProfilePic)
def profile_pics_deletion_notification(sender, instance, **kwargs):
    """Method that handles the notification for profile pics deletion"""
    user = instance.user
    action = f"Profile Pics was deleted for User: {instance.user.username}"
    send_notification(user, action, notification_type="general")
    notification_event.set()


@receiver(post_save, sender=CoverPhoto)
def cover_photo_creation_notification(sender, instance, created, **kwargs):
    """Method that handles notification for cover photo upload"""
    if created:
        action = f"Cover photo uploaded for user: {instance.user.username}"
        send_notification(instance.user, action, notification_type="general")
        notification_event.set()


@receiver(post_delete, sender=CoverPhoto)
def cover_photo_deletion_notification(sender, instance, **kwargs):
    """Method that handles notification for cover photo deletion"""
    action = f"Cover photo deleted for user: {instance.user.username}"
    send_notification(instance.user, action, notification_type="general")
    notification_event.set()


@receiver(post_save, sender=Follow)
def follow_notification(sender, instance, created, **kwargs):
    """Method that handles notification when a user is followed"""
    action = f"{instance.follower.username} followed  {instance.followed.username}"
    send_notification(instance.user, action, notification_type="follow")
    notification_event.set()


@receiver(post_delete, sender=Follow)
def unfollow_notification(sender, instance, **kwargs):
    """Method that handles notification when a user is unfollowed"""
    action = f"{instance.follower.username} unfollowed {instance.followed.username}"
    send_notification(instance.user, action, notification_type="unfollow")

    notification_event.set()


@receiver(post_save, sender=User)
def profile_update_notification(sender, instance, created, **kwargs):
    """Method that handles notification when a user profile is updated"""
    if not created:
        action = f"User profile updated: {instance.username}"
        send_notification(instance, action, notification_type="general")
        notification_event.set()


@receiver(post_delete, sender=User)
def profile_deletion_notification(sender, instance, **kwargs):
    """Method that handles notification when a user profile is deleted"""
    action = f"User profile deleted: {instance.username}"
    send_notification(instance, action, notification_type="general")
    notification_event.set()
