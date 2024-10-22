# Generated by Django 4.2 on 2024-10-22 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_post_hashtags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='hashtags',
            field=models.ManyToManyField(blank=True, related_name='hashing_posts', to='posts.hashtag'),
        ),
    ]
