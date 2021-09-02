# Generated by Django 2.2 on 2021-08-31 08:53

import core.mixinsModels
import django.contrib.postgres.fields.jsonb
import django.core.validators
from django.db import migrations, models
import master_data.models
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('code', core.mixinsModels.UpperCaseCharField(max_length=50, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('description', models.TextField(blank=True, default='')),
                ('is_active', models.BooleanField(default=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'db_table': 'category',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Cell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=500)),
                ('code', core.mixinsModels.UpperCaseCharField(max_length=500, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('description', models.TextField(blank=True, null=True)),
                ('cell_acv', models.DecimalField(decimal_places=6, default=0, max_digits=15)),
                ('num_universe', models.DecimalField(decimal_places=6, default=0, max_digits=15)),
                ('optimal_panel', models.IntegerField(default=0)),
                ('condition_html', models.TextField(blank=True, null=True)),
                ('serialize_str', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Cell',
                'verbose_name_plural': 'Cells',
                'db_table': 'cell',
            },
        ),
        migrations.CreateModel(
            name='Census',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('censusdata', django.contrib.postgres.fields.jsonb.JSONField()),
                ('heads', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
            options={
                'verbose_name': 'Census',
                'verbose_name_plural': 'Censuses',
                'db_table': 'census',
            },
        ),
        migrations.CreateModel(
            name='IndexCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'verbose_name': 'Index Category',
                'verbose_name_plural': 'Index Categries',
                'db_table': 'index_category',
            },
        ),
        migrations.CreateModel(
            name='Month',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(choices=[('January', 'January'), ('February', 'February'), ('March', 'March'), ('Aapril', 'Aapril'), ('May', 'May'), ('June', 'June'), ('July', 'July'), ('August', 'August'), ('September', 'September'), ('October', 'October'), ('November', 'November'), ('December', 'December')], max_length=150)),
                ('code', core.mixinsModels.UpperCaseCharField(max_length=50, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('date', models.DateField(blank=True, null=True)),
                ('month', models.SmallIntegerField()),
                ('year', models.SmallIntegerField()),
                ('is_locked', models.BooleanField(default=True)),
                ('is_current_month', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Mont',
                'verbose_name_plural': 'Months',
                'db_table': 'month',
                'ordering': ['month', 'year'],
            },
        ),
        migrations.CreateModel(
            name='Outlet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('code', core.mixinsModels.UpperCaseCharField(max_length=50, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('insert_date', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'verbose_name': 'Outlet',
                'verbose_name_plural': 'Outlets',
                'db_table': 'outlet',
            },
        ),
        migrations.CreateModel(
            name='OutletType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('code', core.mixinsModels.UpperCaseCharField(max_length=50, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('urbanity', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.TextField(blank=True, default='', null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
            ],
            options={
                'verbose_name': 'Outlet Type',
                'verbose_name_plural': 'Outlet Types',
                'db_table': 'outlet_type',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PanelProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('hand_nhand', models.CharField(blank=True, max_length=50, null=True)),
                ('region', models.CharField(blank=True, max_length=50, null=True)),
                ('outlet_status', models.CharField(blank=True, max_length=50, null=True)),
                ('audit_date', models.DateField(blank=True, null=True)),
                ('wtd_factor', models.DecimalField(decimal_places=6, default=0, max_digits=15)),
                ('num_factor', models.DecimalField(decimal_places=6, default=0, max_digits=15)),
                ('turnover', models.DecimalField(decimal_places=6, default=0, max_digits=15)),
                ('custom_channel_1', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_2', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_3', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_4', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_5', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_6', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_7', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_8', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_9', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_10', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_11', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_12', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_13', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_14', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_15', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_16', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_17', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_18', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_19', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_20', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_21', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_22', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_23', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_24', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_25', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_26', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_27', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_28', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_29', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_30', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_31', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_32', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_33', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_34', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_35', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_36', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_37', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_38', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_39', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_40', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_41', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_42', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_43', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_44', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_45', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_46', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_47', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_48', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_49', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_channel_50', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_1', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_2', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_3', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_4', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_5', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_6', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_7', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_8', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_9', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_10', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_11', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_12', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_13', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_14', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_15', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_16', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_17', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_18', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_19', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_20', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_21', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_22', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_23', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_24', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_25', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_26', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_27', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_28', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_29', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_30', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_31', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_32', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_33', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_34', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_35', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_36', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_37', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_38', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_39', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_40', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_41', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_42', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_43', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_44', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_45', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_46', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_47', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_48', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_49', models.CharField(blank=True, max_length=80, null=True)),
                ('custom_region_50', models.CharField(blank=True, max_length=80, null=True)),
            ],
            options={
                'verbose_name': 'PanelProfile',
                'verbose_name_plural': 'PanelProfiles',
                'db_table': 'panel_profile',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('code', core.mixinsModels.UpperCaseCharField(max_length=50, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('pack_type', models.CharField(blank=True, max_length=150, null=True)),
                ('aggregation_level', models.CharField(blank=True, max_length=150, null=True)),
                ('company', models.CharField(blank=True, max_length=150, null=True)),
                ('brand', models.CharField(blank=True, max_length=150, null=True)),
                ('family', models.CharField(blank=True, max_length=150, null=True)),
                ('flavour_type', models.CharField(blank=True, max_length=150, null=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=6, max_digits=15, null=True)),
                ('price_segment', models.CharField(blank=True, max_length=150, null=True)),
                ('length_range', models.CharField(blank=True, max_length=150, null=True)),
                ('number_in_pack', models.IntegerField(blank=True, null=True)),
                ('price_per_stick', models.DecimalField(blank=True, decimal_places=6, max_digits=15, null=True)),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'db_table': 'product',
            },
        ),
        migrations.CreateModel(
            name='ProductAudit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('period', models.CharField(blank=True, max_length=50, null=True)),
                ('product_details', models.TextField(blank=True, null=True)),
                ('avaibility', models.BooleanField(default=True)),
                ('facing_empty', models.IntegerField(default=0)),
                ('facing_not_empty', models.IntegerField(default=0)),
                ('forward', models.IntegerField(default=0)),
                ('reserve', models.IntegerField(default=0)),
                ('total_none_empty_facing_forward_reserve', models.IntegerField(default=0)),
                ('purchaseother1', models.IntegerField(default=0)),
                ('purchaseother2', models.IntegerField(default=0)),
                ('purchasediary', models.IntegerField(default=0)),
                ('purchaseinvoice', models.IntegerField(default=0)),
                ('price_in_unit', models.DecimalField(decimal_places=6, max_digits=15)),
                ('price_in_pack', models.DecimalField(decimal_places=6, max_digits=15)),
                ('priceother', models.DecimalField(decimal_places=6, max_digits=15)),
                ('cash_discount', models.DecimalField(decimal_places=6, max_digits=15)),
                ('product_foc', models.IntegerField(default=0)),
                ('gift_with_purchase', models.IntegerField(default=0)),
                ('appreciation_award', models.IntegerField(default=0)),
                ('other_trade_promotion', models.IntegerField(default=0)),
                ('sales_unprojected_volume', models.DecimalField(decimal_places=6, default=0, max_digits=15)),
                ('sales_unprojected_value', models.DecimalField(decimal_places=6, default=0, max_digits=15)),
                ('sales_unprojected_units', models.DecimalField(decimal_places=6, default=0, max_digits=15)),
                ('sales_projected_volume', models.DecimalField(decimal_places=6, default=0, max_digits=15)),
                ('sales_projected_value', models.DecimalField(decimal_places=6, default=0, max_digits=15)),
                ('sales_projected_units', models.DecimalField(decimal_places=6, default=0, max_digits=15)),
                ('pack_without_graphic_health_warning', models.IntegerField(default=0)),
                ('no_of_pack_without_graphic_health_warning_facing', models.IntegerField(default=0)),
                ('no_of_pack_without_graphic_health_warning_total_stock', models.IntegerField(default=0)),
                ('no_of_pack_without_none_tax_stamp', models.IntegerField(default=0)),
                ('point_of_sales_signboard', models.IntegerField(default=0)),
                ('point_of_sales_poster', models.IntegerField(default=0)),
                ('point_of_sales_counter_shield', models.IntegerField(default=0)),
                ('point_of_sales_price_sticker', models.IntegerField(default=0)),
                ('point_of_sales_umbrella', models.IntegerField(default=0)),
                ('point_of_sales_counter_top_display', models.IntegerField(default=0)),
                ('point_of_sales_lighter', models.IntegerField(default=0)),
                ('point_of_sales_others', models.IntegerField(default=0)),
                ('point_of_sales_none', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Audit Data',
                'verbose_name_plural': 'Audit Data',
                'db_table': 'product_audit',
            },
        ),
        migrations.CreateModel(
            name='RBD',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=500)),
                ('code', core.mixinsModels.UpperCaseCharField(max_length=500, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('description', models.TextField(blank=True, null=True)),
                ('condition_html', models.TextField(blank=True, null=True)),
                ('serialize_str', models.TextField(blank=True, null=True)),
                ('cell_acv', models.DecimalField(decimal_places=6, default=0, max_digits=15)),
                ('num_universe', models.DecimalField(decimal_places=6, default=0, max_digits=15)),
                ('optimal_panel', models.IntegerField(default=0)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
            ],
            options={
                'verbose_name': 'RBD',
                'verbose_name_plural': 'RBDs',
                'db_table': 'rbd',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('code', core.mixinsModels.UpperCaseCharField(max_length=50, validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('description', models.TextField(blank=True, default='')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
            ],
            options={
                'verbose_name': 'Region',
                'verbose_name_plural': 'Regions',
                'db_table': 'region',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='RegionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=150)),
            ],
            options={
                'verbose_name': 'Region Type',
                'verbose_name_plural': 'Region Types',
                'db_table': 'region_type',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('import_mode', models.CharField(choices=[('APPEND', 'Append: Add records in the table.'), ('UPDATE', 'Update: If records exist update.'), ('APPENDUPDATE', 'Append/Update: If  records exist update otherwise add.'), ('REFRESH', 'Reresh: Delete all records and repopulate from the source.')], max_length=20)),
                ('frommodel', models.CharField(max_length=50)),
                ('file', models.FileField(upload_to=master_data.models.handle_upload_logs)),
                ('is_processing', models.CharField(blank=True, choices=[('UPLOADING', 'Uploading'), ('PROCESSING', 'Processing'), ('COMPLETED', 'Completed'), ('ERROR', 'Error')], max_length=20, null=True)),
                ('process_message', models.CharField(blank=True, max_length=255, null=True)),
                ('skiped_records', models.IntegerField(blank=True, null=True)),
                ('updated_records', models.IntegerField(blank=True, null=True)),
                ('created_records', models.IntegerField(blank=True, null=True)),
                ('log', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Upload',
                'verbose_name_plural': 'Uploads',
                'db_table': 'upload',
            },
        ),
        migrations.CreateModel(
            name='UsableOutlet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'UsableOutlet',
                'verbose_name_plural': 'UsableOutlets',
                'db_table': 'usable_outlet',
            },
        ),
    ]
