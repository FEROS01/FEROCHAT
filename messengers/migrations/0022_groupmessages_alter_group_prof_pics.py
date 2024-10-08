# Generated by Django 4.1.7 on 2023-07-30 12:43

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import messengers.models
import Groups.models


class Migration(migrations.Migration):

    dependencies = [
        ('messengers', '0021_rename_date_added_messages_date_sent'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupMessages',
            fields=[
                ('messages_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE,
                 parent_link=True, primary_key=True, serialize=False, to='messengers.messages')),
            ],
            bases=('messengers.messages',),
        ),
        migrations.AlterField(
            model_name='group',
            name='prof_pics',
            field=models.ImageField(blank=True, null=True, upload_to=Groups.models.group_directory_path, validators=[django.core.validators.validate_image_file_extension, messengers.models.image_type_validator,
                                    messengers.models.file_size_val, django.core.validators.FileExtensionValidator(['gif', 'png', 'jpeg', 'jpg', 'webp', 'avif', 'apng'], 'Unsupported file format. Try a valid image format')]),
        ),
    ]
