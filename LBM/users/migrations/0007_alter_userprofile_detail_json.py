# Generated by Django 4.2.6 on 2023-10-19 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_remove_userprofile_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='detail_json',
            field=models.JSONField(blank=True, null=True),
        ),
    ]