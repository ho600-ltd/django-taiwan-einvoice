# Generated by Django 3.2.10 on 2022-07-22 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0019_update_batch_einvoices'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadbatch',
            name='ei_turnkey_batch_id',
            field=models.PositiveBigIntegerField(default=0),
        ),
    ]
