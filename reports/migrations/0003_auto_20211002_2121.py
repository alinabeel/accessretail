# Generated by Django 2.2 on 2021-10-02 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_auto_20211002_2118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rbdreport',
            name='name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
