# Generated by Django 3.2.14 on 2022-08-02 13:41

from django.db import migrations


def update_invoice_identifier(apps, schema_editor):
    EITurnkeyBatchEInvoice = apps.get_model('turnkey_wrapper', 'EITurnkeyBatchEInvoice')
    for self in EITurnkeyBatchEInvoice.objects.all().order_by('id'):
        mig = self.ei_turnkey_batch.mig
        if "C0401" == mig:
            invoice_date = self.body[self.ei_turnkey_batch.mig]["Main"]["InvoiceDate"]
        elif "C0501" == mig:
            invoice_date = self.body[self.ei_turnkey_batch.mig]["CancelDate"]
        elif "C0701" == mig:
            invoice_date = self.body[self.ei_turnkey_batch.mig]["VoidDate"]
        else:
            raise Exception(_("There is no setting for {}").format(mig))
        self.invoice_identifier = "{mig}{batch_einvoice_track_no}{InvoiceDate}".format(
            mig=mig,
            batch_einvoice_track_no=self.batch_einvoice_track_no,
            InvoiceDate=invoice_date,
        )
        self.save()



class Migration(migrations.Migration):

    dependencies = [
        ('turnkey_wrapper', '0015_auto_20220802_1326'),
    ]

    operations = [
        migrations.RunPython(update_invoice_identifier, lambda x, y: '/dev/null'),
    ]