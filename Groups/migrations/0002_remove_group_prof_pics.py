# Generated by Django 4.1.8 on 2023-09-18 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Groups', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='prof_pics',
        ),
    ]
