# Generated by Django 4.2.6 on 2023-10-20 02:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_partition'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='detail_json',
        ),
    ]
