# Generated by Django 4.2.13 on 2024-12-02 01:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0052_add_F0401_F0501_F0701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicaluploadbatch',
            name='status',
            field=models.CharField(choices=[('0', 'Collecting'), ('1', 'Waiting for trigger(Stop Collecting)'), ('2', 'Noticed to TKW'), ('3', 'Exporting E-Invoice JSON'), ('4', 'Uploaded to TKW'), ('f', 'Finish'), ('-', 'Failed but ignore')], db_index=True, default='0', max_length=1),
        ),
        migrations.AlterField(
            model_name='uploadbatch',
            name='status',
            field=models.CharField(choices=[('0', 'Collecting'), ('1', 'Waiting for trigger(Stop Collecting)'), ('2', 'Noticed to TKW'), ('3', 'Exporting E-Invoice JSON'), ('4', 'Uploaded to TKW'), ('f', 'Finish'), ('-', 'Failed but ignore')], db_index=True, default='0', max_length=1),
        ),
    ]
