# Generated by Django 4.2 on 2024-10-14 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='type',
            field=models.CharField(choices=[('message', 'Message Notification'), ('post', 'Post notification'), ('follow', 'follow notification'), ('unfollow', 'unfollow notification'), ('general', 'General Notification')], default='general', max_length=25),
        ),
    ]
