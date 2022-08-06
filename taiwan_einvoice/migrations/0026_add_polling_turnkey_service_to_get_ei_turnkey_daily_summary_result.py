# Generated by Django 3.2.10 on 2022-08-04 01:50
from django.db import migrations


INITIAL_CRON_FUNCTION = ['taiwan_einvoice.crontabs.polling_turnkey_service_to_get_and_create_ei_turnkey_daily_summary_result', ]

def forward(apps, schema_editor):
    SelectOption = apps.get_model('crontab_monitor', 'SelectOption')
    Inspection = apps.get_model('crontab_monitor', 'Inspection')
    for value in INITIAL_CRON_FUNCTION:
        cf_so = SelectOption(swarm='cron-function', value=value)
        cf_so.save()

    insp = Inspection(
        cron_format='37 0-4,17-23 * * *',
        name="polling_TK_to_get_ei_turnkey_daily_summary_result",
        function_option=cf_so,
        function_note="Polling TurnkeyService to get and create summary report"
    )
    insp.save()


def backward(apps, schema_editor):
    SelectOption = apps.get_model('crontab_monitor', 'SelectOption')
    Inspection = apps.get_model('crontab_monitor', 'Inspection')
    insp = Inspection.objects.filter(name="polling_turnkey_service_to_get_and_create_ei_turnkey_daily_summary_result",
                                     function_option__value__in=INITIAL_CRON_FUNCTION)
    insp.delete()

    cf_sos = SelectOption.objects.filter(swarm='cron-function', value__in=INITIAL_CRON_FUNCTION)
    cf_sos.delete()



class Migration(migrations.Migration):

    dependencies = [
        ('taiwan_einvoice', '0025_alter_turnkeyservice_options'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]