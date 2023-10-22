# Generated by Django 4.2.6 on 2023-10-22 18:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_userprofile_get_bank_account_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partition',
            name='current_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=20),
        ),
    ]
