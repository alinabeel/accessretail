# Generated by Django 2.2 on 2022-01-17 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master_data', '0018_auto_20220114_1018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usableoutlet',
            name='status',
            field=models.CharField(choices=[('USABLE', 'Usable'), ('NOTUSABLE', 'Not Usable'), ('DROP', 'Drop'), ('QUARANTINE', 'Quarantine')], default='USABLE', max_length=20),
        ),
    ]
