# -*- coding: utf-8 -*-
import logging, urllib, time, datetime, re, decimal, operator
from django.db.models import Q, Count, Sum
from django.utils.translation import gettext as _
from django.utils.timezone import now
from crontab_monitor.models import SelectOption
from taiwan_einvoice.models import UploadBatch


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
        if status[0] in ['c', 'm']:
            continue
        ubs_pair = UploadBatch.status_check(statuss=status[0])
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