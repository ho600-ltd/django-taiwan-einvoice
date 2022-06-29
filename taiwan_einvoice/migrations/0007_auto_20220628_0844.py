# Generated by Django 3.2.10 on 2022-06-28 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0006_auto_20220624_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='canceleinvoice',
            name='new_einvoice',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='new_einvoice_on_cancel_einvoice_set', to='taiwan_einvoice.einvoice'),
        ),
        migrations.AlterField(
            model_name='einvoice',
            name='carrier_type',
            field=models.CharField(choices=[('3J0002', 'Mobile barcode'), ('CQ0001', 'Natural Person')], db_index=True, default='', max_length=6),
        ),
        migrations.AlterField(
            model_name='voideinvoice',
            name='new_einvoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='new_einvoice_on_void_einvoice_set', to='taiwan_einvoice.einvoice'),
        ),
    ]