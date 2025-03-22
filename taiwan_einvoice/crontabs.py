# -*- coding: utf-8 -*-
import logging, urllib, time, datetime, re, decimal, operator
from django.db.models import Q, Count, Sum
from django.utils.translation import gettext as _
from django.utils.timezone import now
from crontab_monitor.models import SelectOption
from taiwan_einvoice.models import TurnkeyService, UploadBatch, SummaryReport, SellerInvoiceTrackNo


def polling_upload_batch(alert_log, *args, **kw):
    lg = logging.getLogger('info')
    lg.debug("alert_log id: {}".format(alert_log.id))
    lg.debug("*args: {}".format(args))
    lg.debug("**kw: {}".format(kw))
    title = _('There is no alarm in polling_upload_batch, just logging')
    mail_body = "Executed from {}\n".format(kw.get('executed_from', '__none__'))
    mail_body += "args: {}\n".format(args)
    mail_body += "kw: {}\n".format(kw)

    NOW = now()
    t0 = time.time()

    alert_log_status = SelectOption.objects.get(swarm='alert-log-status', value='LOG')

    for status in UploadBatch.status_choices:
        if status[0] in ['-', ]:
            continue
        ubs_pair = UploadBatch.status_check(statuss=[status[0]])
        for up in ubs_pair:
            title = _('Executed polling_upload_batch')
            _s = "Executed {}.{} from {} to {}".format(*up)
            lg.debug(_s)
            mail_body += _s + "\n"
        lg.debug("UploadBatch.status_check({}) end at {}".format(status[0], now()))

    lg.debug("UploadBatch.status_check end at {}".format(now()))

    alert_log.title = title
    alert_log.mail_body = _("Title: {title}".format(title=title)) + "\n\n" + mail_body
    alert_log.status = alert_log_status
    alert_log.executed_end_time = now()
    alert_log.save()
    lg.debug("title: {}".format(alert_log.title))
    lg.debug("status: {}".format(alert_log.status))


def polling_turnkey_service_to_get_and_create_ei_turnkey_daily_summary_result(alert_log, *args, **kw):
    lg = logging.getLogger('info')
    lg.debug("alert_log id: {}".format(alert_log.id))
    lg.debug("*args: {}".format(args))
    lg.debug("**kw: {}".format(kw))
    title = _('There is no alarm in polling_turnkey_service_to_get_and_create_ei_turnkey_daily_summary_result, just logging')
    mail_body = "Executed from {}\n".format(kw.get('executed_from', '__none__'))
    mail_body += "args: {}\n".format(args)
    mail_body += "kw: {}\n".format(kw)

    NOW = now()
    t0 = time.time()

    alert_log_status = SelectOption.objects.get(swarm='alert-log-status', value='LOG')

    for turnkey_service in TurnkeyService.objects.exclude(Q(tkw_endpoint='')|Q(tkw_endpoint__isnull=True)).order_by('routing_id'):
        title = _('Executed polling_turnkey_service_to_get_and_create_ei_turnkey_daily_summary_result')
        _s = str(turnkey_service.get_and_create_ei_turnkey_daily_summary_result())
        lg.debug(_s)
        mail_body += _s + "\n"
        lg.debug("{turnkey_service}.get_and_create_ei_turnkey_daily_summary_result end at {now}".format(turnkey_service=turnkey_service, now=now()))

    lg.debug("polling_turnkey_service_to_get_and_create_ei_turnkey_daily_summary_result end at {}".format(now()))

    alert_log.title = title
    alert_log.mail_body = _("Title: {title}".format(title=title)) + "\n\n" + mail_body
    alert_log.status = alert_log_status
    alert_log.executed_end_time = now()
    alert_log.save()
    lg.debug("title: {}".format(alert_log.title))
    lg.debug("status: {}".format(alert_log.status))


def polling_turnkey_service_to_get_and_create_ei_turnkey_e0501_invoice_assign_no(alert_log, *args, **kw):
    lg = logging.getLogger('info')
    lg.debug("alert_log id: {}".format(alert_log.id))
    lg.debug("*args: {}".format(args))
    lg.debug("**kw: {}".format(kw))
    title = _('There is no alarm in polling_turnkey_service_to_get_and_create_ei_turnkey_e0501_invoice_assign_no, just logging')
    mail_body = "Executed from {}\n".format(kw.get('executed_from', '__none__'))
    mail_body += "args: {}\n".format(args)
    mail_body += "kw: {}\n".format(kw)

    NOW = now()
    t0 = time.time()

    alert_log_status = SelectOption.objects.get(swarm='alert-log-status', value='LOG')

    for turnkey_service in TurnkeyService.objects.exclude(Q(tkw_endpoint='')|Q(tkw_endpoint__isnull=True)).order_by('routing_id'):
        title = _('Executed polling_turnkey_service_to_get_and_create_ei_turnkey_e0501_invoice_assign_no')
        _s = str(turnkey_service.get_and_create_ei_turnkey_e0501_invoice_assign_no())
        lg.debug(_s)
        mail_body += _s + "\n"
        lg.debug("{turnkey_service}.get_and_create_ei_turnkey_e0501_invoice_assign_no end at {now}".format(turnkey_service=turnkey_service, now=now()))

    lg.debug("polling_turnkey_service_to_get_and_create_ei_turnkey_e0501_invoice_assign_no end at {}".format(now()))

    alert_log.title = title
    alert_log.mail_body = _("Title: {title}".format(title=title)) + "\n\n" + mail_body
    alert_log.status = alert_log_status
    alert_log.executed_end_time = now()
    alert_log.save()
    lg.debug("title: {}".format(alert_log.title))
    lg.debug("status: {}".format(alert_log.status))


def auto_generate_summary_report(alert_log, *args, **kw):
    lg = logging.getLogger('info')
    lg.debug("alert_log id: {}".format(alert_log.id))
    lg.debug("*args: {}".format(args))
    lg.debug("**kw: {}".format(kw))
    title = _('There is no alarm in auto_generate_summary_report, just logging')
    mail_body = "Executed from {}\n".format(kw.get('executed_from', '__none__'))
    mail_body += "args: {}\n".format(args)
    mail_body += "kw: {}\n".format(kw)

    NOW = now()
    t0 = time.time()

    alert_log_status = SelectOption.objects.get(swarm='alert-log-status', value='LOG')

    SummaryReport.auto_generate_report(generate_at_time=NOW)
    title = _('Executed auto_generate_summary_report')
    lg.debug("SummaryReport.auto_generate_report end at {now}".format(now=now()))
    lg.debug("auto_generate_summary_report end at {}".format(now()))

    alert_log.title = title
    alert_log.mail_body = _("Title: {title}".format(title=title)) + "\n\n" + mail_body
    alert_log.status = alert_log_status
    alert_log.executed_end_time = now()
    alert_log.save()
    lg.debug("title: {}".format(alert_log.title))
    lg.debug("status: {}".format(alert_log.status))


def warn_managers_from_the_blank_track_number_is_below_the_threshold(alert_log, *args, **kw):
    lg = logging.getLogger('info')
    lg.debug("alert_log id: {}".format(alert_log.id))
    lg.debug("*args: {}".format(args))
    lg.debug("**kw: {}".format(kw))
    title = _('There is no alarm in remind_managers_that_the_blank_track_number_is_below_the_threshold, just logging')
    mail_body = "Executed from {}\n".format(kw.get('executed_from', '__none__'))
    mail_body += "args: {}\n".format(args)
    mail_body += "kw: {}\n".format(kw)

    NOW = now()
    t0 = time.time()

    alert_log_status = SelectOption.objects.get(swarm='alert-log-status', value='LOG')

    threshold = kw.get('threshold', '0.2')
    Notifications = SellerInvoiceTrackNo.warn_managers_from_the_blank_track_number_is_below_the_threshold(threshold=threshold)
    title = _('Executed remind_managers_that_the_blank_track_number_is_below_the_threshold')
    lg.debug("remind_managers_that_the_blank_track_number_is_below_the_threshold end at {}".format(now()))

    alert_log.title = title
    alert_log.mail_body = _("Title: {title}".format(title=title)) + "\n\n" + mail_body + "\n\nNotifications: " + str(Notifications)
    alert_log.status = alert_log_status
    alert_log.executed_end_time = now()
    alert_log.save()
    lg.debug("title: {}".format(alert_log.title))
    lg.debug("status: {}".format(alert_log.status))