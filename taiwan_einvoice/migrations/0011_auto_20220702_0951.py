# Generated by Django 3.2.10 on 2022-07-02 09:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0010_auto_20220702_0937'),
    ]

    operations = [
        migrations.AddField(
            model_name='einvoice',
            name='mig_type',
            field=models.ForeignKey(default=16, on_delete=django.db.models.deletion.DO_NOTHING, to='taiwan_einvoice.einvoicemig'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='canceleinvoice',
            name='ei_synced',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='canceleinvoice',
            name='generate_time',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='canceleinvoice',
            name='reason',
            field=models.CharField(db_index=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='canceleinvoice',
            name='return_tax_document_number',
            field=models.CharField(blank=True, db_index=True, default='', max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='einvoice',
            name='ei_synced',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='einvoice',
            name='generate_no',
            field=models.CharField(db_index=True, default='', max_length=40),
        ),
        migrations.AlterField(
            model_name='einvoice',
            name='generate_no_sha1',
            field=models.CharField(db_index=True, default='', max_length=10),
        ),
        migrations.AlterField(
            model_name='einvoice',
            name='no',
            field=models.CharField(db_index=True, max_length=8),
        ),
        migrations.AlterField(
            model_name='einvoice',
            name='type',
            field=models.CharField(choices=[('07', 'General'), ('08', 'Special')], db_index=True, default='07', max_length=2),
        ),
        migrations.AlterField(
            model_name='einvoiceprintlog',
            name='done_status',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='einvoiceprintlog',
            name='is_original_copy',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name='einvoiceprintlog',
            name='print_time',
            field=models.DateTimeField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='sellerinvoicetrackno',
            name='begin_no',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='sellerinvoicetrackno',
            name='begin_time',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='sellerinvoicetrackno',
            name='end_no',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='sellerinvoicetrackno',
            name='end_time',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='sellerinvoicetrackno',
            name='track',
            field=models.CharField(db_index=True, max_length=2),
        ),
        migrations.AlterField(
            model_name='sellerinvoicetrackno',
            name='type',
            field=models.CharField(choices=[('07', 'General'), ('08', 'Special')], db_index=True, default='07', max_length=2),
        ),
        migrations.AlterField(
            model_name='voideinvoice',
            name='ei_synced',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='voideinvoice',
            name='generate_time',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='voideinvoice',
            name='reason',
            field=models.CharField(db_index=True, max_length=20),
        ),
    ]
