# Generated by Django 5.1.1 on 2024-09-20 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_user_first_name_user_last_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coverphoto',
            name='image',
            field=models.ImageField(upload_to='images'),
        ),
        migrations.AlterField(
            model_name='profilepic',
            name='image',
            field=models.ImageField(upload_to='images'),
        ),
    ]