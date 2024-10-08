# Generated by Django 4.1.7 on 2023-07-19 00:04

import django.core.validators
from django.db import migrations, models
import messengers.models


class Migration(migrations.Migration):

    dependencies = [
        ('messengers', '0010_alter_friends_date_added'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='friends',
        #     name='friend_date',
        #     field=models.DateTimeField(auto_now=True),
        # ),
        # migrations.AddField(
        #     model_name='info',
        #     name='prof_pics',
        #     field=models.ImageField(blank=True, null=True, upload_to=messengers.models.user_directory_path, validators=[django.core.validators.validate_image_file_extension, messengers.models.image_type_validator, django.core.validators.FileExtensionValidator(['gif', 'png', 'jpeg', 'jpg', 'webp', 'avif', 'apng'], 'Unsupported file format. Try a valid image format')]),
        # ),
        # migrations.AddField(
        #     model_name='info',
        #     name='unread_messages',
        #     field=models.IntegerField(default=0),
        # ),
        # migrations.AddField(
        #     model_name='messages',
        #     name='media',
        #     field=models.FileField(blank=True, null=True, upload_to=messengers.models.user_directory_media, validators=[django.core.validators.FileExtensionValidator(['gif', 'png', 'jpeg', 'jpg', 'webp', 'avif', 'apng', 'mp4', 'webm', 'ogv', 'pdf', 'txt', 'csv', 'json', 'mp3', 'wav', 'oga'], 'Unsupported File format'), messengers.models.file_size_val, messengers.models.file_type_validator]),
        # ),
        # migrations.AddField(
        #     model_name='messages',
        #     name='read',
        #     field=models.BooleanField(default=True),
        # ),
        migrations.AlterField(
            model_name='info',
            name='about',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='info',
            name='bio',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='messages',
            name='text',
            field=models.TextField(blank=True),
        ),
    ]
