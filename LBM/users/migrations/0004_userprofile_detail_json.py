# Generated by Django 4.2.6 on 2023-10-19 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='detail_json',
            field=models.JSONField(default={}),
        ),
    ]