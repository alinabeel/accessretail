# Generated by Django 2.2 on 2021-09-26 00:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0012_auto_20210925_2301'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usableoutlet',
            old_name='staus',
            new_name='status',
        ),
        migrations.RemoveField(
            model_name='usableoutlet',
            name='is_active',
        ),
    ]