# Generated by Django 3.2.10 on 2021-12-23 08:21

from django.db import migrations

NAMES = [
    {"group_name": 'TaiwanEInvoicePrinterAdminGroup',
        "permissions": [
            "taiwan_einvoice.view_escposweb",
            "taiwan_einvoice.view_staffprofile",
        ]},
    {"group_name": 'TaiwanEInvoiceManagerGroup',
        "permissions": [
            "taiwan_einvoice.view_staffprofile",
            "taiwan_einvoice.add_staffprofile",
            "taiwan_einvoice.change_staffprofile",
        ]},
]


def add_three_basic_groups(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    Group = apps.get_model('auth', 'Group')
    for d in NAMES:
        g, is_created = Group.objects.get_or_create(name=d['group_name'])
        g.save()
        for app_pcode in d['permissions']:
            app, pcode = app_pcode.split('.')
            p = Permission.objects.get(codename=pcode)
            g.permissions.add(p)



def remove_three_basic_groups(apps, schema_editor):
    Permission = apps.get_model('auth', 'Permission')
    Group = apps.get_model('auth', 'Group')
    for d in NAMES:
        g = Group.objects.get(name=d['group_name'])
        g.delete()


def add_default_legalentity(apps, schema_editor):
    LegalEntity = apps.get_model('taiwan_einvoice', 'LegalEntity')
    le, is_created = LegalEntity.objects.get_or_create(identifier='0000000000')
    le.name = '0000000000'
    le.save()


def remove_default_legalentity(apps, schema_editor):
    LegalEntity = apps.get_model('taiwan_einvoice', 'LegalEntity')
    le = LegalEntity.objects.get(identifier='0000000000', name='0000000000')
    le.delete()
class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_three_basic_groups, remove_three_basic_groups),
        migrations.RunPython(add_default_legalentity, remove_default_legalentity),
    ]
