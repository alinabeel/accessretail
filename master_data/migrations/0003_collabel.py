# Generated by Django 2.2 on 2021-09-06 08:30

import core.mixinsModels
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    dependencies = [
        ('master_setups', '0001_initial'),
        ('master_data', '0002_auto_20210906_0803'),
    ]

    operations = [
        migrations.CreateModel(
            name='ColLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('code', core.mixinsModels.UpperCaseCharField(max_length=50, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('col_name', models.CharField(max_length=150)),
                ('col_label', models.CharField(max_length=150)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_setups.Country')),
                ('model_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.District')),
            ],
            options={
                'verbose_name': 'ColLabel',
                'verbose_name_plural': 'ColLabels',
                'db_table': 'col_label',
                'unique_together': {('country', 'code')},
            },
        ),
    ]