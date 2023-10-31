# Generated by Django 4.2.6 on 2023-10-31 18:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0026_remove_partition_owner_partition_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partition',
            name='owner',
        ),
        migrations.AddField(
            model_name='partition',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
