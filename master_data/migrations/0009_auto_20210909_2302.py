# Generated by Django 2.2 on 2021-09-09 23:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0008_auto_20210909_2148'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='panelprofile',
            name='week',
        ),
        migrations.AddField(
            model_name='panelprofile',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='master_data.Category'),
            preserve_default=False,
        ),
    ]
