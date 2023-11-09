# Generated by Django 4.2.6 on 2023-11-09 05:06

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('partitions', '0025_ruleuniopexpression_reference_attr'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rulebiopexpression',
            name='operator',
            field=django_cryptography.fields.encrypt(models.CharField(blank=True, choices=[('eq', 'Equals'), ('lt', 'Less Than'), ('gt', 'Greater Than'), ('lte', 'Less Than or Equal'), ('gte', 'Greater Than or Equal')], max_length=20, null=True)),
        ),
        migrations.DeleteModel(
            name='Rule',
        ),
    ]
