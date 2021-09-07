# Generated by Django 2.2 on 2021-09-06 08:03

import core.mixinsModels
from django.conf import settings
import django.contrib.auth.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('1', 'Country Manager'), ('2', 'Manager'), ('3', 'Superwiser'), ('4', 'Auditor')], default='1', max_length=20)),
                ('username', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                ('email', models.CharField(max_length=50, unique=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('state', models.CharField(blank=True, max_length=50, null=True)),
                ('zip', models.CharField(blank=True, max_length=50, null=True)),
                ('country', models.CharField(blank=True, max_length=50, null=True)),
                ('phone_no', models.CharField(blank=True, max_length=50, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'db_table': 'user',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=150)),
                ('code', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Country',
                'verbose_name_plural': 'Countries',
                'db_table': 'country',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='IndexSetup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('code', core.mixinsModels.UpperCaseCharField(max_length=50, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('description', models.TextField(max_length=300)),
                ('is_active', models.BooleanField(default=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_setups.Country')),
            ],
            options={
                'verbose_name': 'Index Setup',
                'verbose_name_plural': 'Index Setups',
                'db_table': 'index_setup',
                'ordering': ['name'],
                'unique_together': {('country', 'code')},
            },
        ),
        migrations.CreateModel(
            name='UserCountry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_setups.Country')),
                ('user', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'UserCountry',
                'verbose_name_plural': 'User Countries',
                'db_table': 'user_country',
            },
        ),
        migrations.CreateModel(
            name='Threshold',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('audited_data_purchase_min', models.DecimalField(blank=True, decimal_places=2, default='-10', max_digits=11, null=True)),
                ('audited_data_purchase_max', models.DecimalField(blank=True, decimal_places=2, default='10', max_digits=11, null=True)),
                ('audited_data_stock_min', models.DecimalField(blank=True, decimal_places=2, default='-10', max_digits=11, null=True)),
                ('audited_data_stock_max', models.DecimalField(blank=True, decimal_places=2, default='10', max_digits=11, null=True)),
                ('audited_data_price_min', models.DecimalField(blank=True, decimal_places=2, default='-10', max_digits=11, null=True)),
                ('audited_data_price_max', models.DecimalField(blank=True, decimal_places=2, default='10', max_digits=11, null=True)),
                ('audited_data_sales_min', models.DecimalField(blank=True, decimal_places=2, default='-10', max_digits=11, null=True)),
                ('audited_data_sales_max', models.DecimalField(blank=True, decimal_places=2, default='10', max_digits=11, null=True)),
                ('outlet_factor_numaric_min', models.DecimalField(blank=True, decimal_places=2, default='0', max_digits=11, null=True)),
                ('outlet_factor_numaric_max', models.DecimalField(blank=True, decimal_places=2, default='1', max_digits=11, null=True)),
                ('country', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='master_setups.Country')),
            ],
            options={
                'verbose_name': 'Threshold',
                'verbose_name_plural': 'Thresholds',
                'db_table': 'threshold',
            },
        ),
        migrations.CreateModel(
            name='CountrySetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='logos')),
                ('timezone', models.CharField(blank=True, max_length=50, null=True)),
                ('country', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='master_setups.Country')),
            ],
            options={
                'verbose_name': 'Country Setting',
                'verbose_name_plural': 'Country Settings',
                'db_table': 'country_setting',
                'ordering': ['country'],
            },
        ),
        migrations.CreateModel(
            name='UserIndex',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_setups.Country')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('user_index', models.ManyToManyField(to='master_setups.IndexSetup')),
            ],
            options={
                'verbose_name': 'User Index',
                'verbose_name_plural': 'User Indexes',
                'db_table': 'user_index',
                'unique_together': {('country', 'user')},
            },
        ),
    ]
