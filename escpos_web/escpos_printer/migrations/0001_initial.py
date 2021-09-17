# Generated by Django 3.2.5 on 2021-09-13 07:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Printer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(max_length=128, unique=True)),
                ('nickname', models.CharField(max_length=64, unique=True)),
                ('type', models.CharField(choices=[('n', 'Network'), ('p', 'Parallel'), ('s', 'Serial'), ('u', 'USB')], max_length=1)),
                ('vendor_number', models.SmallIntegerField()),
                ('product_number', models.SmallIntegerField()),
                ('profile', models.CharField(choices=[('00', 'TM-T88IV'), ('01', 'TM-T88V')], max_length=2)),
                ('receipt_type', models.CharField(choices=[('5', '58mm Receipt'), ('6', '58mm E-Invoice'), ('8', '80mm Receipt')], max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='TEWeb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=755)),
                ('slug', models.CharField(max_length=4)),
                ('hash_key', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meet_to_tw_einvoice_standard', models.BooleanField(default=False)),
                ('track_no', models.CharField(max_length=32)),
                ('generate_time', models.DateTimeField()),
                ('original_width', models.CharField(choices=[('5', '58mm'), ('8', '80mm')], default='5', max_length=1)),
                ('content', models.JSONField()),
                ('te_web', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='escpos_printer.teweb')),
            ],
            options={
                'unique_together': {('meet_to_tw_einvoice_standard', 'track_no')},
            },
        ),
        migrations.CreateModel(
            name='ReceiptLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('copy_order', models.SmallIntegerField(default=0)),
                ('print_time', models.DateTimeField(null=True)),
                ('printer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='escpos_printer.printer')),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='escpos_printer.receipt')),
            ],
            options={
                'unique_together': {('printer', 'receipt', 'copy_order')},
            },
        ),
    ]