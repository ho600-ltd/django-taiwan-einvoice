# Generated by Django 3.2.10 on 2022-06-29 09:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0008_alter_einvoice_carrier_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voideinvoice',
            name='new_einvoice',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='new_einvoice_on_void_einvoice_set', to='taiwan_einvoice.einvoice'),
        ),
    ]