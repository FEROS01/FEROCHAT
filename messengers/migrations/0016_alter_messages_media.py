# Generated by Django 4.1.7 on 2023-07-26 19:59

import django.core.validators
from django.db import migrations, models
import messengers.models


class Migration(migrations.Migration):

    dependencies = [
        ('messengers', '0015_alter_messages_media'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='media',
            field=models.FileField(blank=True, null=True, upload_to=messengers.models.user_directory_media, validators=[django.core.validators.FileExtensionValidator(['gif', 'png', 'jpeg', 'jpg', 'webp', 'avif', 'apng', 'mp4', 'webm', 'ogv', 'pdf', 'txt', 'csv', 'json', 'mp3', 'wav', 'oga'], 'Unsupported File format', code='Invalid format'), messengers.models.file_size_val, messengers.models.file_type_validator]),
        ),
    ]
