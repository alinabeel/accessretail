# Generated by Django 2.2 on 2022-01-28 06:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('master_setups', '0007_delete_threshold'),
        ('master_data', '0030_auto_20220128_0613'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usableoutlet',
            unique_together={('country', 'month', 'index', 'outlet', 'cell')},
        ),
        migrations.RemoveField(
            model_name='usableoutlet',
            name='category',
        ),
    ]