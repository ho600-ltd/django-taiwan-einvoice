# Generated by Django 3.2.14 on 2022-08-01 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('turnkey_wrapper', '0012_eiturnkeybatcheinvoice_upload_to_ei_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eiturnkeybatcheinvoice',
            name='upload_to_ei_time',
            field=models.DateTimeField(null=True),
        ),
    ]