import re
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


    def get_content(self, renderer, data, accepted_media_type, renderer_context):
        request = renderer_context['request']
        t = get_template(self.content_template)
        html = t.render({"data": data}, request)
        return html



class ESCPOSWebHtmlRenderer(TEOriginHTMLRenderer):
    pass



class LegalEntityHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('legalentity_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('legalentity_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class TurnkeyWebHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('turnkeyweb_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('turnkeyweb_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class SellerInvoiceTrackNoHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('sellerinvoicetrackno_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('sellerinvoicetrackno_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_content(self, renderer, data, accepted_media_type, renderer_context):
        t = get_template(self.content_template)
        view = renderer_context['view']
        request = renderer_context['request']
        serializer = self._get_serializer(view.serializer_class, view, request)
        turnkey_web_queryset_in_post_form = serializer.fields['turnkey_web'].get_queryset()
        html = t.render({"data": data,
                         "turnkey_web_options_in_post_form": turnkey_web_queryset_in_post_form,
                        }, request)
        return html



class EInvoiceHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('einvoice_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('einvoice_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class EInvoicePrintLogHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('einvoiceprintlog_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('einvoiceprintlog_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)