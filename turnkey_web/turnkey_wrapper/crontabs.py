# -*- coding: utf-8 -*-
import logging, urllib, time, datetime, re, decimal, operator
from django.db.models import Q, Count, Sum
from django.utils.translation import gettext as _
from django.utils.timezone import now
from crontab_monitor.models import SelectOption
from turnkey_wrapper.models import EITurnkey, EITurnkeyBatch


def polling_ei_turnkey_batch(alert_log, *args, **kw):
    lg = logging.getLogger('info')
    lg.debug("alert_log id: {}".format(alert_log.id))
    lg.debug("*args: {}".format(args))
    lg.debug("**kw: {}".format(kw))
    title = _('There is no alarm in polling_ei_turnkey_batch, just logging')
    mail_body = "Executed from {}\n".format(kw.get('executed_from', '__none__'))
    mail_body += "args: {}\n".format(args)
    mail_body += "kw: {}\n".format(kw)

    NOW = now()
    t0 = time.time()

    alert_log_status = SelectOption.objects.get(swarm='alert-log-status', value='LOG')

    for status in EITurnkeyBatch.status_choices:
        if status[0] not in ['8', '9']:
            continue
        eitbs_pair = EITurnkeyBatch.status_check(statuss=[status[0]])
        for eitb in eitbs_pair:
            title = _('Executed polling_ei_turnkey_batch')
            _s = "Executed {}.{} from {} to {}".format(*eitb)
            lg.debug(_s)
            mail_body += _s + "\n"
        lg.debug("EITurnkeyBatch.status_check({}) end at {}".format(status[0], now()))

    lg.debug("EITurnkeyBatch.status_check end at {}".format(now()))

    alert_log.title = title
    alert_log.mail_body = _("Title: {title}".format(title=title)) + "\n\n" + mail_body
    alert_log.status = alert_log_status
    alert_log.executed_end_time = now()
    alert_log.save()
    lg.debug("title: {}".format(alert_log.title))
    lg.debug("status: {}".format(alert_log.status))


def polling_ei_turnkey(alert_log, *args, **kw):
    lg = logging.getLogger('info')
    lg.debug("alert_log id: {}".format(alert_log.id))
    lg.debug("*args: {}".format(args))
    lg.debug("**kw: {}".format(kw))
    title = _('There is no alarm in polling_ei_turnkey, just logging')
    mail_body = "Executed from {}\n".format(kw.get('executed_from', '__none__'))
    mail_body += "args: {}\n".format(args)
    mail_body += "kw: {}\n".format(kw)

    NOW = now()
    t0 = time.time()

    alert_log_status = SelectOption.objects.get(swarm='alert-log-status', value='LOG')

    title = _('Executed polling_ei_turnkey')
    for summary_result_xml in EITurnkey.parse_summary_result_then_create_objects():
        _s = "Parsed {abspath}: total count: {total_count}, good count: {good_count}, failed count: {failed_count} at {now}".format(
            abspath=summary_result_xml.abspath,
            total_count=summary_result_xml.total_count,
            good_count=summary_result_xml.good_count,
            failed=summary_result_xml.failed_count,
            now=now()
        )
        lg.debug(_s)
        mail_body += _s + "\n"
    lg.debug("EITurnkey.parse_summary_result_then_create_objects() end at {}".format(now()))

    alert_log.title = title
    alert_log.mail_body = _("Title: {title}".format(title=title)) + "\n\n" + mail_body
    alert_log.status = alert_log_status
    alert_log.executed_end_time = now()
    alert_log.save()
    lg.debug("title: {}".format(alert_log.title))
    lg.debug("status: {}".format(alert_log.status))