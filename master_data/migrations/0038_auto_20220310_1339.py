# Generated by Django 2.2 on 2022-03-10 13:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0037_auto_20220203_2316'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auditdata',
            name='avg_sales',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='flag_copied_previous',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='flag_neg_sales_corr',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='flag_outlier',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='flag_price',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='flag_purchse',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='flag_sales',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='flag_stock',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='is_valid',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='price_variation',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='purchase_variation',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='sales_variation',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='sd_sales',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='stock_variation',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='valid_purchase_max',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='valid_purchase_min',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='valid_sales_max',
        ),
        migrations.RemoveField(
            model_name='auditdata',
            name='valid_sales_min',
        ),
    ]