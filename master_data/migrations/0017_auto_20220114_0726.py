# Generated by Django 2.2 on 2022-01-14 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0016_auto_20220114_0432'),
    ]

    operations = [
        migrations.RenameField(
            model_name='panelprofile',
            old_name='common_outlet',
            new_name='flag_accepted_a',
        ),
        migrations.RenameField(
            model_name='panelprofile',
            old_name='copied_outlet',
            new_name='flag_accepted_b',
        ),
        migrations.RenameField(
            model_name='panelprofile',
            old_name='droped_outlet',
            new_name='flag_common_outlet',
        ),
        migrations.RenameField(
            model_name='panelprofilechild',
            old_name='common_outlet',
            new_name='flag_accepted_a',
        ),
        migrations.RenameField(
            model_name='panelprofilechild',
            old_name='copied_outlet',
            new_name='flag_accepted_b',
        ),
        migrations.RenameField(
            model_name='panelprofilechild',
            old_name='droped_outlet',
            new_name='flag_common_outlet',
        ),
        migrations.RemoveField(
            model_name='panelprofile',
            name='new_outlet',
        ),
        migrations.RemoveField(
            model_name='panelprofile',
            name='price_variation',
        ),
        migrations.RemoveField(
            model_name='panelprofilechild',
            name='new_outlet',
        ),
        migrations.RemoveField(
            model_name='panelprofilechild',
            name='price_variation',
        ),
        migrations.AddField(
            model_name='panelprofile',
            name='flag_copied_outlet',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='panelprofile',
            name='flag_droped_a',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='panelprofile',
            name='flag_droped_b',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='panelprofile',
            name='flag_droped_outlet',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='panelprofile',
            name='flag_new_outlet',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='panelprofilechild',
            name='flag_copied_outlet',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='panelprofilechild',
            name='flag_droped_a',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='panelprofilechild',
            name='flag_droped_b',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='panelprofilechild',
            name='flag_droped_outlet',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='panelprofilechild',
            name='flag_new_outlet',
            field=models.BooleanField(default=False),
        ),
    ]
