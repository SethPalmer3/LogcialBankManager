# Generated by Django 4.2.6 on 2023-10-29 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_remove_externalwebapp_user_userprofile_bank'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='get_bank_account',
        ),
        migrations.AddField(
            model_name='externalwebapp',
            name='get_bank_account',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
