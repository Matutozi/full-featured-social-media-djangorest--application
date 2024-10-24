# Generated by Django 4.2 on 2024-10-21 05:41

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0004_postreaction_reaction_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='tagged_users',
            field=models.ManyToManyField(blank=True, related_name='tagged_in_posts', to=settings.AUTH_USER_MODEL),
        ),
    ]