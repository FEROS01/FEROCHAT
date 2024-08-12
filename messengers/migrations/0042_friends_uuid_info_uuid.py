# Generated by Django 4.1.8 on 2024-08-12 15:28

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('messengers', '0041_remove_friends_uuid_remove_info_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='friends',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='info',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
    ]
