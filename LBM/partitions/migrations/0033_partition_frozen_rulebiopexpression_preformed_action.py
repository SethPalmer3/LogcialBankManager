# Generated by Django 4.2.6 on 2023-11-21 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partitions', '0032_remove_rulebiopexpression_transfer_from'),
    ]

    operations = [
        migrations.AddField(
            model_name='partition',
            name='frozen',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rulebiopexpression',
            name='preformed_action',
            field=models.BooleanField(default=False),
        ),
    ]
