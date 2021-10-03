# Generated by Django 2.2 on 2021-09-25 23:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('master_setups', '0001_initial'),
        ('master_data', '0011_auto_20210919_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='usableoutlet',
            name='cell',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='master_data.Cell'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='usableoutlet',
            name='staus',
            field=models.CharField(choices=[('UA', 'Usable'), ('NU', 'Not Usable'), ('DR', 'Drop'), ('QA', 'Quarantine')], default='UA', max_length=2),
        ),
        migrations.AlterUniqueTogether(
            name='usableoutlet',
            unique_together={('country', 'month', 'index', 'outlet', 'cell')},
        ),
    ]