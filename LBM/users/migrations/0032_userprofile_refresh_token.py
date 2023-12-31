# Generated by Django 4.2.6 on 2023-11-03 01:46

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0031_userprofile_access_token_userprofile_last_refreshed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='refresh_token',
            field=django_cryptography.fields.encrypt(models.TextField(max_length=30, null=True)),
        ),
    ]
