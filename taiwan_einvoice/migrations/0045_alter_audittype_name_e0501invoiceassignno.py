# Generated by Django 4.2.4 on 2023-08-04 04:53

from django.db import migrations, models


def create_audit_type(apps, schema_editor):
    AuditType = apps.get_model('taiwan_einvoice', 'AuditType')

    audit_type = AuditType(name='E0501_INVOICE_ASSIGN_NO')
    audit_type.save()


def remove_audit_type(apps, schema_editor):
    AuditType = apps.get_model('taiwan_einvoice', 'AuditType')

    AuditType.objects.filter(name='E0501_INVOICE_ASSIGN_NO').delete()




class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0044_alter_printer_receipt_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audittype',
            name='name',
            field=models.CharField(choices=[('TEA_CEC_PROCESSING', 'TEA/CEC Processing'), ('UPLOAD_TO_EITURNKEY', 'Upload to EITurnkey'), ('EITURNKEY_PROCESSING', 'EITurnkey Processing'), ('EI_PROCESSING', 'EI Processing'), ('EI_PROCESSED', 'EI Processed'), ('EI_SUMMARY_RESULT', 'EI Summary Result'), ('E0501_INVOICE_ASSIGN_NO', 'E0501(Invoice Assign No)')], max_length=32, unique=True),
        ),
        migrations.CreateModel(
            name='E0501InvoiceAssignNo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('identifier', models.CharField(db_index=True, max_length=8)),
                ('type', models.CharField(choices=[('07', 'General'), ('08', 'Special')], db_index=True, default='07', max_length=2)),
                ('year_month', models.CharField(db_index=True, max_length=5)),
                ('track', models.CharField(db_index=True, max_length=2)),
                ('begin_no', models.CharField(db_index=True, max_length=8)),
                ('end_no', models.CharField(db_index=True, max_length=8)),
            ],
            options={
                'unique_together': {('identifier', 'type', 'year_month', 'track', 'begin_no', 'end_no')},
            },
        ),
        migrations.RunPython(create_audit_type, remove_audit_type),
    ]
