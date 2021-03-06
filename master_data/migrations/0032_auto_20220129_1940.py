# Generated by Django 2.2 on 2022-01-29 19:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master_setups', '0007_delete_threshold'),
        ('master_data', '0031_auto_20220128_0616'),
    ]

    operations = [
        migrations.AddField(
            model_name='outletcensus',
            name='index',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='master_setups.IndexSetup'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='outletcensus',
            unique_together={('country', 'outlet', 'index', 'category')},
        ),
    ]
