# Generated by Django 3.2.14 on 2022-08-02 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('turnkey_wrapper', '0013_alter_eiturnkeybatcheinvoice_upload_to_ei_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='eiturnkey',
            name='can_sync_to_ei',
            field=models.BooleanField(default=False),
        ),
    ]
