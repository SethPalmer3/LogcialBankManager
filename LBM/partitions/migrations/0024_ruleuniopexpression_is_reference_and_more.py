# Generated by Django 4.2.6 on 2023-11-08 18:55

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('partitions', '0023_remove_rulebiopexpression_parent_expr_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ruleuniopexpression',
            name='is_reference',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ruleuniopexpression',
            name='reference_id',
            field=django_cryptography.fields.encrypt(models.CharField(blank=True, max_length=30, null=True)),
        ),
        migrations.AddField(
            model_name='ruleuniopexpression',
            name='reference_type',
            field=django_cryptography.fields.encrypt(models.CharField(blank=True, max_length=50, null=True)),
        ),
    ]