# Generated by Django 2.2 on 2021-10-15 12:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0026_auto_20211015_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cityvillage',
            name='upload',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='master_data.Upload'),
        ),
    ]
