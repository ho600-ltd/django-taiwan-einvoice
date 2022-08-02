import re, logging
import string

from datetime import datetime
from io import BytesIO

from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from rest_framework.renderers import BrowsableAPIRenderer, HTMLFormRenderer

from taiwan_einvoice.models import TurnkeyService, SummaryReport, TEAlarm


def _get_template_name(template_name, sub_dir='', show_template_filename=False, lang=''):
    """ finding order: (sub_dir, langs) > (sub_dir) > (langs) > ()
    """
    import os, itertools
    from django.conf import settings
    from django.utils.translation import get_language
    from django.template import TemplateDoesNotExist

    if not lang: lang = get_language()
    if not template_name.endswith('.html'): template_name += '.html'
    lg = logging.getLogger('info')

    _langs = [lang] + [l[0] for l in settings.LANGUAGES[:]]
    langs = []
    for _lang in _langs:
        if _lang and _lang not in langs: langs.append(_lang)
    lg.debug(langs)

    orders = [
        [[sub_dir], langs],
        [[sub_dir]],
        [langs],
        [],
    ]
    t = None
    for order in orders:
        lg.debug(order)
        _L = list(itertools.product(*order))
        for _l in _L:
            _l = list(_l) + [template_name]
            lg.debug("_l: {}".format(_l))
            _path = os.path.join(*_l)
            lg.debug("_path: {}".format(_path))
            try:
                temp_template = get_template(_path)
            except (TemplateDoesNotExist, TypeError):
                continue
            else:
                t = os.path.join(_path)
                break
        if t:
            break
    if show_template_filename:
        lg.info('Use template: "%s"' % t)

    return t



class TEBrowsableAPIRenderer(BrowsableAPIRenderer):
    template = "taiwan_einvoice/api.html"



class TEOriginHTMLRenderer(TEBrowsableAPIRenderer):
    template = _get_template_name('escposweb_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('escposweb_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)
    format = 'html'


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        res['data'] = data
        return  res


    def get_content(self, renderer, data, accepted_media_type, renderer_context):
        if getattr(data.get('detail', ''), 'code', ''):
            return data['detail']
        request = renderer_context['request']
        t = get_template(self.content_template)
        html = t.render({"data": data}, request)
        return html



class ESCPOSWebHtmlRenderer(TEOriginHTMLRenderer):
    pass



class ESCPOSWebOperatorHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('escposweboperator_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('escposweboperator_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class StaffProfileHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('staffprofile_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('staffprofile_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class LegalEntityHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('legalentity_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('legalentity_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class TurnkeyServiceHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('turnkeyservice_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('turnkeyservice_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class TurnkeyServiceGroupHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('turnkeyservicegroup_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('turnkeyservicegroup_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_content(self, renderer, data, accepted_media_type, renderer_context):
        if getattr(data.get('detail', ''), 'code', ''):
            return data['detail']
        from taiwan_einvoice.models import TurnkeyService
        request = renderer_context['request']
        t = get_template(self.content_template)
        if data.get('id', None):
            object = TurnkeyService.objects.get(id=data['id'])
        else:
            object = None
        html = t.render({"data": data, "object": object}, request)
        return html


class SellerInvoiceTrackNoHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('sellerinvoicetrackno_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('sellerinvoicetrackno_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_content(self, renderer, data, accepted_media_type, renderer_context):
        if getattr(data.get('detail', ''), 'code', ''):
            return data['detail']
        t = get_template(self.content_template)
        view = renderer_context['view']
        request = renderer_context['request']
        html = t.render({"data": data,
                        }, request)
        return html



class EInvoiceHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('einvoice_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('einvoice_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class EInvoicePrintLogHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('einvoiceprintlog_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('einvoiceprintlog_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class CancelEInvoiceHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('canceleinvoice_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('canceleinvoice_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class VoidEInvoiceHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('voideinvoice_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('voideinvoice_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class AuditLogHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('auditlog_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('auditlog_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        res['turnkey_services'] = TurnkeyService.objects.all().order_by('id')
        return  res




class UploadBatchHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('uploadbatch_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('uploadbatch_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class BatchEInvoiceHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('batcheinvoice_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('batcheinvoice_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class SummaryReportHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('summaryreport_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('summaryreport_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        res['turnkey_services'] = TurnkeyService.objects.all().order_by('id')
        res['report_type_choices'] = SummaryReport.report_type_choices
        return  res



class TEAlarmHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('tealarm_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('tealarm_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        res['turnkey_services'] = TurnkeyService.objects.all().order_by('id')
        res['target_audience_type_choices'] = TEAlarm.target_audience_type_choices
        return  res


