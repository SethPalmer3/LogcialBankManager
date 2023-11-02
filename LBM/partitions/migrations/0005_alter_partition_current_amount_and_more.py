# Generated by Django 4.2.6 on 2023-11-02 05:29

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('partitions', '0004_alter_partition_label'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partition',
            name='current_amount',
            field=django_cryptography.fields.encrypt(models.DecimalField(decimal_places=2, default=0.0, max_digits=20)),
        ),
        migrations.AlterField(
            model_name='partition',
            name='description',
            field=django_cryptography.fields.encrypt(models.CharField(blank=True, default='', max_length=1000)),
        ),
    ]
