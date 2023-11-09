# Generated by Django 4.2.6 on 2023-11-07 19:57

from django.db import migrations, models
import django.db.models.deletion
import django_cryptography.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('partitions', '0010_alter_partitionrule_action_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='partitionrule',
            name='condition_type',
        ),
        migrations.AlterField(
            model_name='partitionrule',
            name='action_type',
            field=django_cryptography.fields.encrypt(models.CharField(choices=[('fix', 'Fix Amount')], max_length=50)),
        ),
        migrations.AlterField(
            model_name='partitionrule',
            name='action_value',
            field=django_cryptography.fields.encrypt(models.CharField(max_length=50)),
        ),
        migrations.AlterField(
            model_name='partitionrule',
            name='condition_value_attribute',
            field=django_cryptography.fields.encrypt(models.CharField(choices=[('init_amount', 'Inital Amount'), ('current_amount', 'Current Amount')], max_length=50)),
        ),
        migrations.AlterField(
            model_name='partitionrule',
            name='name',
            field=django_cryptography.fields.encrypt(models.CharField(max_length=20)),
        ),
        migrations.CreateModel(
            name='RuleExpression',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('operator', models.CharField(choices=[('add', 'Add'), ('sub', 'Subtract'), ('eq', 'Equals'), ('lt', 'Less Than'), ('gt', 'Greater Than'), ('and', 'And'), ('or', 'Or'), ('identity', 'Value')], max_length=50)),
                ('value', django_cryptography.fields.encrypt(models.CharField(max_length=100))),
                ('left_expression', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='left_expr', to='partitions.ruleexpression')),
                ('parent_expression', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent_expr', to='partitions.ruleexpression')),
                ('right_expression', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='right_expr', to='partitions.ruleexpression')),
            ],
        ),
        migrations.AlterField(
            model_name='partitionrule',
            name='condition_value',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='partitions.ruleexpression'),
        ),
    ]