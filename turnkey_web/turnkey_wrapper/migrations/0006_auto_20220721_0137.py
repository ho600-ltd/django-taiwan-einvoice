# Generated by Django 3.2.14 on 2022-07-21 01:37

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('turnkey_wrapper', '0005_auto_20220718_0817'),
    ]

    operations = [
        migrations.AddField(
            model_name='eiturnkeybatcheinvoice',
            name='batch_einvoic_begin_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 21, 1, 37, 16, 198918, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eiturnkeybatcheinvoice',
            name='batch_einvoic_end_time',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 21, 1, 37, 19, 236455, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='eiturnkeybatcheinvoice',
            name='batch_einvoic_track_no',
            field=models.CharField(default='NO24634102', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='eiturnkeybatch',
            name='status',
            field=models.CharField(choices=[('7', 'Just created'), ('8', 'Downloaded from TEA'), ('9', 'Exported to Data/'), ('P', 'Preparing for EI(P)'), ('G', 'Uploaded to EI or Downloaded from EI(G)'), ('E', 'E Error for EI process(E)'), ('I', 'I Error for EI process(I)'), ('C', 'Successful EI process(C)'), ('M', 'Swith to Successful EI process manually(S-C)')], db_index=True, default='7', max_length=1),
        ),
    ]
