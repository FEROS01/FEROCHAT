# Generated by Django 4.1.8 on 2024-08-12 15:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Groups', '0005_group_uuid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='uuid',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='uuid',
        ),
    ]
