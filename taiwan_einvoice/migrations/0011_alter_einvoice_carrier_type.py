# Generated by Django 3.2.8 on 2021-11-22 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0010_auto_20211122_0907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='einvoice',
            name='carrier_type',
            field=models.CharField(choices=[('3J0002', 'Mobile barcode')], db_index=True, default='', max_length=6),
        ),
    ]
