# Generated by Django 3.2.10 on 2022-08-06 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0031_alter_summaryreport_report_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaluploadbatch',
            name='kind',
            field=models.CharField(choices=[('wp', 'Wait for printed'), ('cp', 'Could print'), ('np', 'No need to print'), ('57', 'Wait for C0501 or C0701'), ('w4', 'Wait for C0401'), ('54', 'Wait for C0501 or C0401'), ('E', 'E0401 ~ E0501')], max_length=2),
        ),
        migrations.AlterField(
            model_name='uploadbatch',
            name='kind',
            field=models.CharField(choices=[('wp', 'Wait for printed'), ('cp', 'Could print'), ('np', 'No need to print'), ('57', 'Wait for C0501 or C0701'), ('w4', 'Wait for C0401'), ('54', 'Wait for C0501 or C0401'), ('E', 'E0401 ~ E0501')], max_length=2),
        ),
    ]
