# Generated by Django 4.1.8 on 2024-08-05 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messengers', '0038_info_dark_theme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='info',
            name='dark_theme',
            field=models.BooleanField(default=False),
        ),
    ]
