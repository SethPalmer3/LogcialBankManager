# Generated by Django 4.2.6 on 2023-11-02 05:29

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_delete_partition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='externalwebapp',
            name='client_key',
            field=django_cryptography.fields.encrypt(models.CharField(max_length=200)),
        ),
        migrations.AlterField(
            model_name='externalwebapp',
            name='get_bank_account',
            field=django_cryptography.fields.encrypt(models.JSONField(blank=True, null=True)),
        ),
        migrations.AlterField(
            model_name='externalwebapp',
            name='secret_key',
            field=django_cryptography.fields.encrypt(models.CharField(max_length=200)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='total_amount',
            field=django_cryptography.fields.encrypt(models.DecimalField(decimal_places=2, max_digits=30, null=True)),
        ),
    ]