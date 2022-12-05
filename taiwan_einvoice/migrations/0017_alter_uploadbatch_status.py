# Generated by Django 3.2.10 on 2022-07-19 02:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0016_auditlog_audittype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='uploadbatch',
            name='status',
            field=models.CharField(choices=[('0', 'Collecting'), ('1', 'Waiting for trigger(Stop Collecting)'), ('2', 'Noticed to TKW'), ('3', 'Exporting E-Invoice Body'), ('4', 'Uploaded to TKW'), ('p', 'Preparing for EI(P)'), ('g', 'Uploaded to EI or Downloaded from EI(G)'), ('e', 'E Error for EI process(E)'), ('i', 'I Error for EI process(I)'), ('c', 'Successful EI process(C)'), ('m', 'Swith to Successful EI process manually(S-C)')], db_index=True, default='0', max_length=1),
        ),
    ]
