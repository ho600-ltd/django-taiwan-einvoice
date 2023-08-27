import re, logging
import string

from datetime import datetime
from io import BytesIO

from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy

from guardian.shortcuts import get_objects_for_user, get_perms
from rest_framework.renderers import BrowsableAPIRenderer, HTMLFormRenderer

from taiwan_einvoice.models import (User,
                                    Seller,
                                    TurnkeyService,
                                    SellerInvoiceTrackNo,
                                    EInvoice,
                                    CancelEInvoice,
                                    VoidEInvoice,
                                    Printer,
                                    EInvoicePrintLog,
                                    UploadBatch,
                                    BatchEInvoice,
                                    SummaryReport,
                                    TEAlarm,
                                    AuditType,
                                    )


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



class TEAStaffProfileHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('teastaffprofile_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('teastaffprofile_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_content(self, renderer, data, accepted_media_type, renderer_context):
        if getattr(data.get('detail', ''), 'code', ''):
            return data['detail']
        request = renderer_context['request']
        turnkey_services = get_objects_for_user(request.user, ["taiwan_einvoice.view_turnkeyservice",], any_perm=True)
        t = get_template(self.content_template)
        html = t.render({"data": data, "turnkey_service_names": [ts.name for ts in turnkey_services]}, request)
        return html



class LegalEntityHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('legalentity_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('legalentity_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)



class TurnkeyServiceHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('turnkeyservice_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('turnkeyservice_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        turnkey_services = get_objects_for_user(res['request'].user, ["taiwan_einvoice.view_turnkeyservice",], any_perm=True)
        seller_ids = turnkey_services.values_list('seller', flat=True)
        res['seller__legal_entity__identifiers'] = Seller.objects.filter(id__in=seller_ids).order_by('legal_entity__identifier').values_list('legal_entity__identifier', flat=True)
        return  res



class TurnkeyServiceGroupHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('turnkeyservicegroup_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('turnkeyservicegroup_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_content(self, renderer, data, accepted_media_type, renderer_context):
        if getattr(data.get('detail', ''), 'code', ''):
            return data['detail']
        from taiwan_einvoice.models import TurnkeyService
        from taiwan_einvoice.permissions import CanEditTurnkeyServiceGroup
        request = renderer_context['request']
        t = get_template(self.content_template)
        if data.get('id', None):
            permissions = CanEditTurnkeyServiceGroup.ACTION_PERMISSION_MAPPING.get("partial_update", [])
            res = get_objects_for_user(request.user, permissions, any_perm=True).filter(id=data['id'])
            if res:
                object_can_edit_te_turnkeyservicegroup = res.get()
            else:
                object_can_edit_te_turnkeyservicegroup = None
        else:
            object_can_edit_te_turnkeyservicegroup = None
        html = t.render({"data": data, "object_can_edit_te_turnkeyservicegroup": object_can_edit_te_turnkeyservicegroup}, request)
        return html



class SellerInvoiceTrackNoHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('sellerinvoicetrackno_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('sellerinvoicetrackno_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        turnkey_services = get_objects_for_user(res['request'].user, ["taiwan_einvoice.view_te_sellerinvoicetrackno",], any_perm=True)
        res['turnkey_services'] = turnkey_services.order_by('id')
        seller_ids = turnkey_services.values_list('seller', flat=True)
        res['seller__legal_entity__identifiers'] = Seller.objects.filter(id__in=seller_ids).order_by('legal_entity__identifier').values_list('legal_entity__identifier', flat=True)
        res['type_choices'] = SellerInvoiceTrackNo.type_choices
        return  res



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


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        turnkey_services = get_objects_for_user(res['request'].user, ["taiwan_einvoice.view_te_einvoice",], any_perm=True)
        res['turnkey_services'] = turnkey_services.order_by('id')
        seller_ids = turnkey_services.values_list('seller', flat=True)
        res['seller__legal_entity__identifiers'] = Seller.objects.filter(id__in=seller_ids).order_by('legal_entity__identifier').values_list('legal_entity__identifier', flat=True)
        res['type_choices'] = SellerInvoiceTrackNo.type_choices
        creator_ids = EInvoice.objects.filter(seller_invoice_track_no__turnkey_service__in=turnkey_services).values_list("creator", flat=True)
        res['creators'] = User.objects.filter(id__in=creator_ids).order_by('first_name')
        return  res



class EInvoicePrintLogHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('einvoiceprintlog_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('einvoiceprintlog_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        turnkey_services = get_objects_for_user(res['request'].user, ["taiwan_einvoice.view_te_einvoice",], any_perm=True)
        res['turnkey_services'] = turnkey_services.order_by('id')
        seller_ids = turnkey_services.values_list('seller', flat=True)
        res['seller__legal_entity__identifiers'] = Seller.objects.filter(id__in=seller_ids).order_by('legal_entity__identifier').values_list('legal_entity__identifier', flat=True)
        user_ids = EInvoicePrintLog.objects.filter(einvoice__seller_invoice_track_no__turnkey_service__in=turnkey_services).values_list("user", flat=True)
        res['users'] = User.objects.filter(id__in=user_ids).order_by('first_name')
        printer_ids = EInvoicePrintLog.objects.filter(einvoice__seller_invoice_track_no__turnkey_service__in=turnkey_services).values_list("printer", flat=True)
        res['printers'] = Printer.objects.filter(id__in=printer_ids).order_by('nickname')
        creator_ids = EInvoicePrintLog.objects.filter(einvoice__seller_invoice_track_no__turnkey_service__in=turnkey_services).values_list("einvoice__creator", flat=True)
        res['creators'] = User.objects.filter(id__in=creator_ids).order_by('first_name')
        return  res



class CancelEInvoiceHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('canceleinvoice_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('canceleinvoice_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        turnkey_services = get_objects_for_user(res['request'].user, ["taiwan_einvoice.view_te_canceleinvoice",], any_perm=True)
        creator_ids = CancelEInvoice.objects.filter(einvoice__seller_invoice_track_no__turnkey_service__in=turnkey_services).values_list("creator", flat=True)
        res['creators'] = User.objects.filter(id__in=creator_ids).order_by('first_name')
        return  res



class VoidEInvoiceHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('voideinvoice_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('voideinvoice_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        turnkey_services = get_objects_for_user(res['request'].user, ["taiwan_einvoice.view_te_voideinvoice",], any_perm=True)
        creator_ids = VoidEInvoice.objects.filter(einvoice__seller_invoice_track_no__turnkey_service__in=turnkey_services).values_list("creator", flat=True)
        res['creators'] = User.objects.filter(id__in=creator_ids).order_by('first_name')
        return  res



class AuditLogHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('auditlog_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('auditlog_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        turnkey_services = get_objects_for_user(res['request'].user, [
            "taiwan_einvoice.view_te_sellerinvoicetrackno",
            "taiwan_einvoice.view_te_einvoice",
            "taiwan_einvoice.view_te_canceleinvoice",
            "taiwan_einvoice.view_te_voideinvoice",
            "taiwan_einvoice.view_te_einvoiceprintlog",
            "taiwan_einvoice.view_te_summaryreport",
            "taiwan_einvoice.view_turnkeyservice",
            ], any_perm=True)
        res['turnkey_services'] = turnkey_services.order_by('id')
        res['type_choices'] = AuditType.name_choices
        return  res




class UploadBatchHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('uploadbatch_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('uploadbatch_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        turnkey_services = get_objects_for_user(res['request'].user, ["taiwan_einvoice.view_te_alarm_for_programmer",], any_perm=True)
        res['turnkey_services'] = turnkey_services.order_by('id')
        seller_ids = turnkey_services.values_list('seller', flat=True)
        res['seller__legal_entity__identifiers'] = Seller.objects.filter(id__in=seller_ids).order_by('legal_entity__identifier').values_list('legal_entity__identifier', flat=True)
        res['status_choices'] = UploadBatch.status_choices
        res['kind_choices'] = UploadBatch.kind_choices
        return  res



class BatchEInvoiceHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('batcheinvoice_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('batcheinvoice_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        turnkey_services = get_objects_for_user(res['request'].user, ["taiwan_einvoice.view_te_alarm_for_programmer",], any_perm=True)
        res['turnkey_services'] = turnkey_services.order_by('id')
        seller_ids = turnkey_services.values_list('seller', flat=True)
        res['seller__legal_entity__identifiers'] = Seller.objects.filter(id__in=seller_ids).order_by('legal_entity__identifier').values_list('legal_entity__identifier', flat=True)
        res['status_choices'] = BatchEInvoice.status_choices
        return  res


class SummaryReportHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('summaryreport_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('summaryreport_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        turnkey_services = get_objects_for_user(res['request'].user, [
            "taiwan_einvoice.view_te_summaryreport",
            ], any_perm=True)
        res['turnkey_services'] = turnkey_services.order_by('id')
        res['report_type_choices'] = SummaryReport.report_type_choices
        return  res



class TEAlarmHtmlRenderer(TEOriginHTMLRenderer):
    template = _get_template_name('tealarm_list', sub_dir='taiwan_einvoice', show_template_filename=True)
    content_template = _get_template_name('tealarm_list_content', sub_dir='taiwan_einvoice', show_template_filename=True)


    def get_context(self, data, accepted_media_type, renderer_context):
        res = super().get_context(data, accepted_media_type, renderer_context)
        turnkey_services = get_objects_for_user(res['request'].user, [
            "taiwan_einvoice.view_te_alarm_for_general_user",
            "taiwan_einvoice.view_te_alarm_for_programmer",
            ], any_perm=True)
        res['turnkey_services'] = turnkey_services.order_by('id')
        res['target_audience_type_choices'] = TEAlarm.target_audience_type_choices
        return  res


