# Generated by Django 4.2.6 on 2023-11-08 20:35

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('partitions', '0024_ruleuniopexpression_is_reference_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruleuniopexpression',
            name='reference_attr',
            field=django_cryptography.fields.encrypt(models.CharField(blank=True, max_length=50, null=True)),
        ),
    ]
