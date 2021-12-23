# Generated by Django 3.2.10 on 2021-12-23 08:21

from django.db import migrations


NAMES = [
    'TaiwanEInvoiceWorkerGroup',
    'TaiwanEInvoicePrinterGroup',
    'TaiwanEInvoiceManagerGroup',
]


def add_three_basic_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in NAMES:
        g = Group(name=name)
        g.save()


def remove_three_basic_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    for name in NAMES:
        g = Group.objects.get(name=name)
        g.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_three_basic_groups, remove_three_basic_groups)
    ]
