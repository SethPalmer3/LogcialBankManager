# Generated by Django 4.2.6 on 2023-10-24 03:26

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_alter_partition_current_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partition',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, max_digits=30, null=True),
        ),
    ]
