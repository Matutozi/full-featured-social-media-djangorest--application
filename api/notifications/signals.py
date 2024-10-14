from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NotificationSetting
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_notification_settings(sender, instance, created, **kwargs):
    if created:
        NotificationSetting.objects.create(user=instance, enable=True, keywords=[])
