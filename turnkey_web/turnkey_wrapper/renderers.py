import re, logging
import string

from datetime import datetime
from io import BytesIO

from django.template.loader import get_template
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from rest_framework.renderers import BaseRenderer, BrowsableAPIRenderer, HTMLFormRenderer


from turnkey_wrapper.models import EI_STATUSS, MIG_NOS, FROM_CONFIG, EITurnkey, EITurnkeyBatch, EITurnkeyBatchEInvoice


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



class XMLFileRenderer(BaseRenderer):
    media_type = 'text/xml'
    format = 'xml'


    def render(self, data, accepted_media_type=None, renderer_context=None):
        return smart_str(data, encoding=self.charset)



class PlainFileRenderer(BaseRenderer):
    media_type = 'text/plain'
    format = 'plain'


    def render(self, data, accepted_media_type=None, renderer_context=None):
        return smart_str(data, encoding=self.charset)



class TKWBrowsableAPIRenderer(BrowsableAPIRenderer):
    template = "turnkey_wrapper/api.html"



class TKWOriginHTMLRenderer(TKWBrowsableAPIRenderer):
    template = _get_template_name('FROM_CONFIG_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('FROM_CONFIG_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)
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



class FROM_CONFIGHtmlRenderer(TKWOriginHTMLRenderer):
    pass



class SCHEDULE_CONFIGHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('SCHEDULE_CONFIG_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('SCHEDULE_CONFIG_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)



class SIGN_CONFIGHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('SIGN_CONFIG_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('SIGN_CONFIG_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)



class TASK_CONFIGHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('TASK_CONFIG_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('TASK_CONFIG_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)



class TO_CONFIGHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('TO_CONFIG_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('TO_CONFIG_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)



class TURNKEY_MESSAGE_LOGHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('TURNKEY_MESSAGE_LOG_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('TURNKEY_MESSAGE_LOG_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        res['ei_statuss'] = EI_STATUSS
        res['mig_nos'] = MIG_NOS
        res['from_configs'] = FROM_CONFIG.objects.all().order_by('ROUTING_ID')
        return  res



class TURNKEY_MESSAGE_LOG_DETAILHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('TURNKEY_MESSAGE_LOG_DETAIL_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('TURNKEY_MESSAGE_LOG_DETAIL_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        res['ei_statuss'] = EI_STATUSS
        return  res



class TURNKEY_SEQUENCEHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('TURNKEY_SEQUENCE_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('TURNKEY_SEQUENCE_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)



class TURNKEY_SYSEVENT_LOGHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('TURNKEY_SYSEVENT_LOG_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('TURNKEY_SYSEVENT_LOG_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)



class TURNKEY_TRANSPORT_CONFIGHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('TURNKEY_TRANSPORT_CONFIG_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('TURNKEY_TRANSPORT_CONFIG_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)



class TURNKEY_USER_PROFILEHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('TURNKEY_USER_PROFILE_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('TURNKEY_USER_PROFILE_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)



class EITurnkeyHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('eiturnkey_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('eiturnkey_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)



class EITurnkeyBatchHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('eiturnkeybatch_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('eiturnkeybatch_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        res['status_choices'] = EITurnkeyBatch.status_choices
        res['party_ids'] = EITurnkey.objects.all().values_list('party_id', flat=True)
        return  res




class EITurnkeyBatchEInvoiceHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('eiturnkeybatcheinvoice_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('eiturnkeybatcheinvoice_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)



    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        res['status_choices'] = EITurnkeyBatchEInvoice.status_choices
        res['party_ids'] = EITurnkey.objects.all().values_list('party_id', flat=True)
        return  res



class EITurnkeyDailySummaryResultXMLHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('eiturnkeydailysummaryresultxml_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('eiturnkeydailysummaryresultxml_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)



    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        res['ei_turnkeys'] = EITurnkey.objects.all().order_by('routing_id')
        return  res



class EITurnkeyDailySummaryResultHtmlRenderer(TKWOriginHTMLRenderer):
    template = _get_template_name('eiturnkeydailysummaryresult_list', sub_dir='turnkey_wrapper', show_template_filename=True)
    content_template = _get_template_name('eiturnkeydailysummaryresult_list_content', sub_dir='turnkey_wrapper', show_template_filename=True)



    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        res['ei_turnkeys'] = EITurnkey.objects.all().order_by('routing_id')
        return  res


