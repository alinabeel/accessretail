# Generated by Django 2.2 on 2021-09-02 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0010_auto_20210902_0902'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cityvillage',
            name='player_tag',
        ),
        migrations.AddField(
            model_name='cityvillage',
            name='player_tag',
            field=models.ManyToManyField(to='master_data.PlayerTag'),
        ),
    ]