# Generated by Django 4.2.6 on 2023-11-11 01:48

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('partitions', '0027_alter_rulebiopexpression_operator'),
    ]

    operations = [
        migrations.AddField(
            model_name='rulebiopexpression',
            name='label',
            field=django_cryptography.fields.encrypt(models.CharField(blank=True, max_length=20, null=True)),
        ),
    ]
