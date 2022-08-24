# Generated by Django 3.2.10 on 2022-08-24 08:12

from django.db import migrations


def add_0000000000(apps, schema_editor):
    LegalEntity = apps.get_model('taiwan_einvoice', 'LegalEntity')
    GENERAL_CONSUMER_IDENTIFIER = 10*'0'
    le = LegalEntity.objects.get_or_create(identifier=GENERAL_CONSUMER_IDENTIFIER, name=GENERAL_CONSUMER_IDENTIFIER)


class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0037_auto_20220813_0238'),
    ]

    operations = [
        migrations.RunPython(add_0000000000, lambda x, y: '/dev/null'),
    ]
