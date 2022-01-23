# Generated by Django 2.2 on 2022-01-14 04:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0014_auto_20220113_2056'),
    ]

    operations = [
        migrations.AddField(
            model_name='auditdata',
            name='avg_sales',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='auditdata',
            name='flag_copied_previous',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='auditdata',
            name='flag_neg_sales_corr',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='auditdata',
            name='flag_outlier',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='auditdata',
            name='flag_price',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='auditdata',
            name='is_valid',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='auditdata',
            name='price_variation',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='auditdata',
            name='purchase_variation',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='auditdata',
            name='sales_variation',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='auditdata',
            name='sd_sales',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='auditdata',
            name='stock_variation',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='auditdata',
            name='valid_purchase_max',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='auditdata',
            name='valid_purchase_min',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='auditdata',
            name='valid_sales_max',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=11, null=True),
        ),
        migrations.AddField(
            model_name='auditdata',
            name='valid_sales_min',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=11, null=True),
        ),
    ]