# Generated by Django 4.2.6 on 2023-11-03 02:42

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0035_alter_userprofile_last_refreshed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='access_token',
            field=django_cryptography.fields.encrypt(models.TextField(blank=True, max_length=30, null=True)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='last_refreshed',
            field=django_cryptography.fields.encrypt(models.DateTimeField(blank=True, null=True)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='refresh_token',
            field=django_cryptography.fields.encrypt(models.TextField(blank=True, max_length=30, null=True)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='token_type',
            field=django_cryptography.fields.encrypt(models.TextField(blank=True, max_length=30, null=True)),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='total_amount',
            field=django_cryptography.fields.encrypt(models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True)),
        ),
    ]
