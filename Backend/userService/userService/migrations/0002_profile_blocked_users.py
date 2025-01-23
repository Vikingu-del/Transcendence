# Generated by Django 5.1.5 on 2025-01-23 18:07

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userService', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='blocked_users',
            field=models.ManyToManyField(related_name='blocked_users', to=settings.AUTH_USER_MODEL),
        ),
    ]
