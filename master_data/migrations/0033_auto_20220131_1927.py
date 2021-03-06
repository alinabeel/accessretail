# Generated by Django 2.2 on 2022-01-31 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0032_auto_20220129_1940'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='threshold',
            name='drop_outlet_copied',
        ),
        migrations.RemoveField(
            model_name='threshold',
            name='drop_outlet_copied_once',
        ),
        migrations.RemoveField(
            model_name='threshold',
            name='drop_outlet_copy_once_drop_status_code',
        ),
        migrations.AddField(
            model_name='panelprofile',
            name='flag_drop_outlet_copied',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='panelprofilechild',
            name='flag_drop_outlet_copied',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='threshold',
            name='drop_outlet_copy_once_status',
            field=models.CharField(default='0,0', help_text='Status Code of Copy Once Dropped NC/PC  Stores - if Store is weighted Store in the MBD', max_length=250),
        ),
    ]
