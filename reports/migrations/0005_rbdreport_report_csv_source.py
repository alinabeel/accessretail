# Generated by Django 2.2 on 2021-10-03 15:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0004_rbdreport_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='rbdreport',
            name='report_csv_source',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]