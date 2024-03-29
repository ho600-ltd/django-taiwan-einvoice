# Generated by Django 3.2.10 on 2022-07-30 09:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('taiwan_einvoice', '0022_auto_20220729_0656'),
    ]

    operations = [
        migrations.CreateModel(
            name='EInvoicesContentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('', 'Waiting'), ('p', 'Preparing for EI(P)'), ('g', 'Uploaded to EI or Downloaded from EI(G)'), ('e', 'E Error for EI process(E)'), ('i', 'I Error for EI process(I)'), ('c', 'Successful EI process(C)')], db_index=True, default='', max_length=1)),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='contenttypes.contenttype')),
            ],
        ),
        migrations.AlterModelOptions(
            name='turnkeyservice',
            options={'permissions': (('edit_te_turnkeyservicegroup', 'Edit the groups of TurnkeyService'), ('view_te_sellerinvoicetrackno', 'View Seller Invoice Track No'), ('add_te_sellerinvoicetrackno', 'Add Seller Invoice Track No'), ('delete_te_sellerinvoicetrackno', 'Delete Seller Invoice Track No'), ('view_te_einvoice', 'View E-Invoice'), ('view_te_canceleinvoice', 'View Cancel E-Invoice'), ('add_te_canceleinvoice', 'Add Cancel E-Invoice'), ('view_te_voideinvoice', 'View Void E-Invoice'), ('add_te_voideinvoice', 'Add Void E-Invoice'), ('view_te_einvoiceprintlog', 'View E-Invoice Print Log'), ('view_te_alarm_for_general_user', 'View Alarm for the General User'), ('view_te_alarm_for_programmer', 'View Alarm for the Programmer'))},
        ),
        migrations.AddField(
            model_name='canceleinvoice',
            name='mig_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='taiwan_einvoice.einvoicemig'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='voideinvoice',
            name='mig_type',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.DO_NOTHING, to='taiwan_einvoice.einvoicemig'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='TEAlarm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('target_audience_type', models.CharField(choices=[('g', 'General User'), ('p', 'Programmer')], max_length=1)),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField()),
                ('object_id', models.PositiveIntegerField(default=0)),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='contenttypes.contenttype')),
                ('turnkey_service', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='taiwan_einvoice.turnkeyservice')),
                ('viewers', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalUploadBatch',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('create_time', models.DateTimeField(blank=True, db_index=True, editable=False)),
                ('update_time', models.DateTimeField(blank=True, db_index=True, editable=False)),
                ('slug', models.CharField(db_index=True, max_length=14)),
                ('kind', models.CharField(choices=[('wp', 'Wait for printed'), ('cp', 'Could print'), ('np', 'No need to print'), ('57', 'Wait for C0501 or C0701'), ('w4', 'Wait for C0401'), ('54', 'Wait for C0501 or C0401')], max_length=2)),
                ('status', models.CharField(choices=[('0', 'Collecting'), ('1', 'Waiting for trigger(Stop Collecting)'), ('2', 'Noticed to TKW'), ('3', 'Exporting E-Invoice JSON'), ('4', 'Uploaded to TKW'), ('f', 'Finish')], db_index=True, default='0', max_length=1)),
                ('ei_turnkey_batch_id', models.PositiveBigIntegerField(default=0)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('executor', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('mig_type', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='taiwan_einvoice.einvoicemig')),
                ('turnkey_service', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='taiwan_einvoice.turnkeyservice')),
            ],
            options={
                'verbose_name': 'historical upload batch',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalBatchEInvoice',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(default=0)),
                ('begin_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('track_no', models.CharField(max_length=10)),
                ('body', models.JSONField()),
                ('status', models.CharField(choices=[('', 'Waiting'), ('p', 'Preparing for EI(P)'), ('g', 'Uploaded to EI or Downloaded from EI(G)'), ('e', 'E Error for EI process(E)'), ('i', 'I Error for EI process(I)'), ('c', 'Successful EI process(C)')], db_index=True, default='', max_length=1)),
                ('result_code', models.CharField(db_index=True, default='', max_length=5)),
                ('pass_if_error', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('batch', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='taiwan_einvoice.uploadbatch')),
                ('content_type', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='contenttypes.contenttype')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical batch e invoice',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='SummaryReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('begin_time', models.DateTimeField(db_index=True)),
                ('end_time', models.DateTimeField(db_index=True)),
                ('report_type', models.CharField(choices=[('h', 'Hour'), ('d', 'Day'), ('w', 'Week'), ('m', 'Month'), ('o', 'Odd month ~ Even month'), ('y', 'Year'), ('E', 'Daily summary from EI')], db_index=True, max_length=1)),
                ('good_count', models.SmallIntegerField(default=0)),
                ('failed_count', models.SmallIntegerField(default=0)),
                ('good_counts', models.JSONField()),
                ('failed_counts', models.JSONField()),
                ('is_resolve', models.BooleanField(default=False)),
                ('resolve_note', models.TextField(default='')),
                ('failed_objects', models.ManyToManyField(related_name='summary_report_set_as_failed_object', to='taiwan_einvoice.EInvoicesContentType')),
                ('good_objects', models.ManyToManyField(related_name='summary_report_set_as_good_object', to='taiwan_einvoice.EInvoicesContentType')),
                ('resolver', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('turnkey_service', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='taiwan_einvoice.turnkeyservice')),
            ],
            options={
                'unique_together': {('turnkey_service', 'begin_time', 'report_type')},
            },
        ),
    ]
