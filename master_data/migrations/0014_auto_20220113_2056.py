# Generated by Django 2.2 on 2022-01-13 20:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master_setups', '0007_delete_threshold'),
        ('master_data', '0013_threshold_drop_store_copy_once_drop_status_code'),
    ]

    operations = [
        migrations.RenameField(
            model_name='threshold',
            old_name='drop_store_copy_once_drop_status_code',
            new_name='drop_outlet_copy_once_drop_status_code',
        ),
        migrations.CreateModel(
            name='OutletCensus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True, null=True)),
                ('sales', models.IntegerField(blank=True, default=0, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.Category')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_setups.Country')),
                ('index', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_setups.IndexSetup')),
                ('month', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.Month')),
                ('outlet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='master_data.Outlet')),
            ],
            options={
                'verbose_name': 'Outlet Census',
                'verbose_name_plural': 'Outlets Census',
                'db_table': 'outlet_census',
                'unique_together': {('country', 'index', 'category', 'outlet')},
            },
        ),
    ]
