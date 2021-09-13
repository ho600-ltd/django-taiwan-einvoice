# Generated by Django 3.2.5 on 2021-09-13 08:55

from django.db import migrations, models
import django.db.models.deletion
import taiwan_einvoice.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ESCPOSWeb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('slug', models.CharField(default='', max_length=5)),
                ('hash_key', models.CharField(default='', max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='LegalEntity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(db_index=True, max_length=8)),
                ('name', models.CharField(db_index=True, default='', max_length=60)),
                ('address', models.CharField(db_index=True, default='', max_length=100)),
                ('person_in_charge', models.CharField(db_index=True, default='', max_length=30)),
                ('telephone_number', models.CharField(db_index=True, default='', max_length=26)),
                ('facsimile_number', models.CharField(db_index=True, default='', max_length=26)),
                ('email_address', models.CharField(db_index=True, default='', max_length=80)),
                ('customer_number_char', models.CharField(db_index=True, default='', max_length=20)),
                ('role_remark', models.CharField(db_index=True, default='', max_length=40)),
            ],
            options={
                'unique_together': {('identifier', 'customer_number_char')},
            },
            bases=(models.Model, taiwan_einvoice.models.IdentifierRule),
        ),
        migrations.CreateModel(
            name='Seller',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('print_with_seller_optional_fields', models.BooleanField(default=False)),
                ('print_with_buyer_optional_fields', models.BooleanField(default=False)),
                ('legal_entity', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='taiwan_einvoice.legalentity')),
            ],
        ),
        migrations.CreateModel(
            name='TurnkeyWeb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('hash_key', models.CharField(max_length=40)),
                ('transport_id', models.CharField(max_length=10)),
                ('party_id', models.CharField(max_length=10)),
                ('routing_id', models.CharField(max_length=39)),
            ],
        ),
        migrations.CreateModel(
            name='SellerInvoiceTrackNo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('07', 'General'), ('08', 'Special')], default='07', max_length=2)),
                ('begin_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('track', models.CharField(max_length=2)),
                ('begin_no', models.SmallIntegerField()),
                ('end_no', models.SmallIntegerField()),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='taiwan_einvoice.seller')),
                ('turnkey_web', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='taiwan_einvoice.turnkeyweb')),
            ],
        ),
        migrations.CreateModel(
            name='Printer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('serial_number', models.CharField(max_length=128, unique=True)),
                ('nickname', models.CharField(max_length=64, unique=True)),
                ('receipt_type', models.CharField(choices=[('5', '58mm Receipt'), ('6', '58mm E-Invoice'), ('8', '80mm Receipt')], max_length=1)),
                ('escpos_web', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='taiwan_einvoice.escposweb')),
            ],
        ),
        migrations.CreateModel(
            name='ESCPOSWebConnectionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('seed', models.CharField(max_length=15)),
                ('escpos_web', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='taiwan_einvoice.escposweb')),
            ],
            options={
                'unique_together': {('escpos_web', 'seed')},
            },
        ),
        migrations.CreateModel(
            name='EInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('07', 'General'), ('08', 'Special')], default='07', max_length=2)),
                ('track', models.CharField(db_index=True, max_length=2)),
                ('no', models.SmallIntegerField(db_index=True)),
                ('npoban', models.CharField(db_index=True, default='', max_length=7)),
                ('print_mark', models.BooleanField(default=False)),
                ('random_number', models.CharField(db_index=True, max_length=4)),
                ('generate_time', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('seller_identifier', models.CharField(db_index=True, max_length=8)),
                ('seller_name', models.CharField(db_index=True, default='', max_length=60)),
                ('seller_address', models.CharField(db_index=True, default='', max_length=100)),
                ('seller_person_in_charge', models.CharField(db_index=True, default='', max_length=30)),
                ('seller_telephone_number', models.CharField(db_index=True, default='', max_length=26)),
                ('seller_facsimile_number', models.CharField(db_index=True, default='', max_length=26)),
                ('seller_email_address', models.CharField(db_index=True, default='', max_length=80)),
                ('seller_customer_number', models.CharField(db_index=True, default='', max_length=20)),
                ('seller_role_remark', models.CharField(db_index=True, default='', max_length=40)),
                ('buyer_identifier', models.CharField(db_index=True, max_length=8)),
                ('buyer_name', models.CharField(db_index=True, default='', max_length=60)),
                ('buyer_address', models.CharField(db_index=True, default='', max_length=100)),
                ('buyer_person_in_charge', models.CharField(db_index=True, default='', max_length=30)),
                ('buyer_telephone_number', models.CharField(db_index=True, default='', max_length=26)),
                ('buyer_facsimile_number', models.CharField(db_index=True, default='', max_length=26)),
                ('buyer_email_address', models.CharField(db_index=True, default='', max_length=80)),
                ('buyer_customer_number', models.CharField(db_index=True, default='', max_length=20)),
                ('buyer_role_remark', models.CharField(db_index=True, default='', max_length=40)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='as_buyer_own_einvoice_set', to='taiwan_einvoice.legalentity')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='as_seller_own_einvoice_set', to='taiwan_einvoice.legalentity')),
                ('seller_invoice_track_no', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='taiwan_einvoice.sellerinvoicetrackno')),
            ],
            options={
                'unique_together': {('seller_invoice_track_no', 'track', 'no')},
            },
        ),
    ]
