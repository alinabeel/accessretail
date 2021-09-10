# Generated by Django 2.2 on 2021-09-10 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0014_auto_20210910_0558'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='panelprofile',
            name='rex_tagging',
        ),
        migrations.RemoveField(
            model_name='panelprofile',
            name='tts_tagging',
        ),
        migrations.AlterField(
            model_name='panelprofile',
            name='nra_tagging',
            field=models.SmallIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='panelprofile',
            name='ra_tagging',
            field=models.SmallIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='panelprofile',
            name='ret_tagging',
            field=models.SmallIntegerField(blank=True, default=0, null=True),
        ),
    ]
