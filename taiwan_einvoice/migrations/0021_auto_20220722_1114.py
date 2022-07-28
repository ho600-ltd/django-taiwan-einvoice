# Generated by Django 3.2.10 on 2022-07-22 11:14

from django.db import migrations, models


NAME_CHOICES = (
    ("EI_PROCESSED", "EI Processed"),
)


def add_audittype(apps, schema_editor):
    AuditType = apps.get_model('taiwan_einvoice', 'AuditType')
    for nc in NAME_CHOICES:
        adt = AuditType(name=nc[0])
        adt.save()



def remove_audittype(apps, schema_editor):
    AuditType = apps.get_model('taiwan_einvoice', 'AuditType')
    for nc in NAME_CHOICES:
        adt = AuditType.objects.get(name=nc[0])
        adt.delete()



class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0020_uploadbatch_ei_turnkey_batch_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='batcheinvoice',
            name='status',
            field=models.CharField(choices=[('', 'Waiting'), ('p', 'Preparing for EI(P)'), ('g', 'Uploaded to EI or Downloaded from EI(G)'), ('e', 'E Error for EI process(E)'), ('i', 'I Error for EI process(I)'), ('c', 'Successful EI process(C)')], db_index=True, default='', max_length=1),
        ),
        migrations.AlterField(
            model_name='audittype',
            name='name',
            field=models.CharField(choices=[('TEA_CEC_PROCESSING', 'TEA/CEC Processing'), ('UPLOAD_TO_EITURNKEY', 'Upload to EITurnkey'), ('EITURNKEY_PROCESSING', 'EITurnkey Processing'), ('EI_PROCESSING', 'EI Processing'), ('EI_PROCESSED', 'EI Processed')], max_length=32, unique=True),
        ),
        migrations.AlterField(
            model_name='uploadbatch',
            name='status',
            field=models.CharField(choices=[('0', 'Collecting'), ('1', 'Waiting for trigger(Stop Collecting)'), ('2', 'Noticed to TKW'), ('3', 'Exporting E-Invoice JSON'), ('4', 'Uploaded to TKW'), ('f', 'Finish')], db_index=True, default='0', max_length=1),
        ),
        migrations.RunPython(
            add_audittype, remove_audittype
        ),
    ]
