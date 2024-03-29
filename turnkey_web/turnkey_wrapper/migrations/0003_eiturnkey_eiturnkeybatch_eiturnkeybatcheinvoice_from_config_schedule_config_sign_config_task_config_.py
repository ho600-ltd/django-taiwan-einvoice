# Generated by Django 3.2.14 on 2022-07-14 04:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('turnkey_wrapper', '0002_create_views'),
    ]

    operations = [
        migrations.CreateModel(
            name='EITurnkey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('execute_abspath', models.CharField(max_length=755)),
                ('data_abspath', models.CharField(max_length=755)),
                ('hash_key', models.CharField(max_length=40)),
                ('transport_id', models.CharField(max_length=10)),
                ('party_id', models.CharField(max_length=10)),
                ('routing_id', models.CharField(max_length=39)),
                ('tea_turnkey_service_endpoint', models.CharField(max_length=755)),
                ('allow_ips', models.JSONField(null=True)),
                ('endpoint', models.CharField(max_length=755, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EITurnkeyBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('update_time', models.DateTimeField(auto_now=True, db_index=True)),
                ('slug', models.CharField(max_length=14, unique=True)),
                ('mig', models.CharField(choices=[('A0101', 'B2B Exchange Invoice'), ('A0102', 'B2B Exchange Invoice Confirm'), ('B0101', 'B2B Exchange Allowance'), ('B0102', 'B2B Exchange Allowance Confirm'), ('A0201', 'B2B Exchange Cancel Invoice'), ('A0202', 'B2B Exchange Cancel Invoice Confirm'), ('B0201', 'B2B Exchange Cancel Allowance'), ('B0202', 'B2B Exchange Cancel Allowance Confirm'), ('A0301', 'B2B Exchange Reject Invoice'), ('A0302', 'B2B Exchange Reject Invoice Confirm'), ('A0401', 'B2B Certificate Invoice'), ('B0401', 'B2B Certificate Allowance'), ('A0501', 'B2B Certificate Cancel Invoice'), ('B0501', 'B2B Certificate Cancel Allowance'), ('A0601', 'B2B Certificate Reject Invoice'), ('C0401', 'B2C Certificate Invoice'), ('C0501', 'B2C Certificate Cancel Invoice'), ('C0701', 'B2C Certificate Void Invoice'), ('D0401', 'B2C Certificate Allowance'), ('D0501', 'B2C Certificate Cancel Allowance'), ('E0401', 'Branch Track'), ('E0402', 'Branch Track Blank'), ('E0501', 'Invoice Assign No')], default='C0401', max_length=5)),
                ('turnkey_version', models.CharField(choices=[('3.2.1', '3.2.1')], default='3.2.1', max_length=8)),
                ('status', models.CharField(choices=[('7', 'Just created'), ('8', 'Download from TEA'), ('9', 'Export to Data/'), ('P', 'Preparing for EI(P)'), ('G', 'Uploaded to EI or Downloaded from EI(G)'), ('E', 'E Error for EI process(E)'), ('I', 'I Error for EI process(I)'), ('C', 'Successful EI process(C)'), ('M', 'Swith to Successful EI process manually(S-C)')], db_index=True, default='7', max_length=1)),
                ('ei_turnkey', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='turnkey_wrapper.eiturnkey')),
            ],
        ),
        migrations.CreateModel(
            name='EITurnkeyBatchEInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.JSONField()),
                ('result_code', models.CharField(db_index=True, default='', max_length=5)),
                ('pass_if_error', models.BooleanField(default=False)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='turnkey_wrapper.eiturnkeybatch')),
            ],
        ),
    ]
