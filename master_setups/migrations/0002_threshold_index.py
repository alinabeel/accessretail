# Generated by Django 2.2 on 2022-01-10 22:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master_setups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='threshold',
            name='index',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='master_setups.IndexSetup'),
            preserve_default=False,
        ),
    ]