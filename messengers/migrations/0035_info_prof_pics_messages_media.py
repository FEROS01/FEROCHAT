# Generated by Django 4.1.8 on 2023-09-18 15:08

import django.core.validators
from django.db import migrations, models
import messengers.models
import messengers.validators


class Migration(migrations.Migration):

    dependencies = [
        ('messengers', '0034_remove_info_prof_pics_remove_messages_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='info',
            name='prof_pics',
            field=models.ImageField(blank=True, null=True, upload_to=messengers.models.user_directory_path, validators=[django.core.validators.validate_image_file_extension, messengers.validators.image_type_validator, messengers.validators.file_size_val, django.core.validators.FileExtensionValidator(['gif', 'png', 'jpeg', 'jpg', 'webp', 'avif', 'apng'], 'Unsupported file format. Try a valid image format')]),
        ),
        migrations.AddField(
            model_name='messages',
            name='media',
            field=models.FileField(blank=True, null=True, upload_to=messengers.models.user_directory_media, validators=[django.core.validators.FileExtensionValidator(['gif', 'png', 'jpeg', 'jpg', 'webp', 'avif', 'apng', 'mp4', 'webm', 'ogv', 'pdf', 'txt', 'csv', 'json', 'mp3', 'wav', 'oga'], 'Unsupported File format', code='Invalid format'), messengers.validators.media_size_val, messengers.validators.file_type_validator]),
        ),
    ]
