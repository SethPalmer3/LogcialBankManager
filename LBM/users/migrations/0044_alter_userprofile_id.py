# Generated by Django 4.2.6 on 2023-11-10 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0043_alter_userprofile_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]