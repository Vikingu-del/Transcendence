# Generated by Django 5.1.5 on 2025-01-20 19:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userService', '0015_remove_chatmodel_receiver_alter_chatmodel_message_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ChatNotification',
        ),
    ]
