# Generated by Django 4.2.6 on 2023-11-21 04:43

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partitions', '0030_rulebiopexpression_transfer_from_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rulebiopexpression',
            name='transfer_amount',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=30),
        ),
    ]
