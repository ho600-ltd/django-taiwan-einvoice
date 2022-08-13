# Generated by Django 3.2.10 on 2022-08-13 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0036_auto_20220809_0651'),
    ]

    operations = [
        migrations.AddField(
            model_name='canceleinvoice',
            name='upload_to_ei_time',
            field=models.DateTimeField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='einvoice',
            name='upload_to_ei_time',
            field=models.DateTimeField(db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='voideinvoice',
            name='upload_to_ei_time',
            field=models.DateTimeField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='historicaluploadbatch',
            name='kind',
            field=models.CharField(choices=[('wp', 'Wait for printed'), ('cp', 'Could print'), ('np', 'No need to print'), ('57', 'Wait for C0501 or C0701'), ('w4', 'Wait for C0401'), ('54', 'Wait for C0501 or C0401'), ('E', 'E0401 ~ E0501'), ('R', 'Re-Created by error status'), ('RN', 'Re-Created by error status with the new track no.')], max_length=2),
        ),
        migrations.AlterField(
            model_name='uploadbatch',
            name='kind',
            field=models.CharField(choices=[('wp', 'Wait for printed'), ('cp', 'Could print'), ('np', 'No need to print'), ('57', 'Wait for C0501 or C0701'), ('w4', 'Wait for C0401'), ('54', 'Wait for C0501 or C0401'), ('E', 'E0401 ~ E0501'), ('R', 'Re-Created by error status'), ('RN', 'Re-Created by error status with the new track no.')], max_length=2),
        ),
    ]
