import re, logging
import string

from datetime import datetime
from io import BytesIO

from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from rest_framework.renderers import BrowsableAPIRenderer, HTMLFormRenderer
from ho600_lib.models import _get_template_name



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



class TurnkeyWebHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('turnkeyweb_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('turnkeyweb_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class TurnkeyWebGroupHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('turnkeywebgroup_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('turnkeywebgroup_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_content(self, renderer, data, accepted_media_type, renderer_context):
        if getattr(data.get('detail', ''), 'code', ''):
            return data['detail']
        from taiwan_einvoice.models import TurnkeyWeb
        request = renderer_context['request']
        t = get_template(self.content_template)
        if data.get('id', None):
            object = TurnkeyWeb.objects.get(id=data['id'])
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


