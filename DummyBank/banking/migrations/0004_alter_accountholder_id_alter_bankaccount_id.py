# Generated by Django 4.2.6 on 2023-10-25 03:27

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0003_accountholder_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountholder',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='bankaccount',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
