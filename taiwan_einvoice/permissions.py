import logging

from rest_framework.permissions import BasePermission, IsAdminUser
from guardian.shortcuts import get_objects_for_user, get_perms

from taiwan_einvoice.models import ESCPOSWeb, TEAlarm



class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_superuser)



class CanEditStaffProfile(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.view_staffprofile",
        ),
        'PATCH': (
            "taiwan_einvoice.change_staffprofile",
        ),
        'POST': (
            "taiwan_einvoice.add_staffprofile",
        )
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanEditStaffProfile.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanEditStaffProfile.has_object_permission with {}: {}".format(request.method, res))
        return res



class CanViewSelfStaffProfile(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.view_staffprofile",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for app_codename in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = app_codename.split('.')
                if codename in get_perms(request.user, request.user.staffprofile):
                    res = True
                    break
        lg.debug("CanViewSelfStaffProfile.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for app_codename in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = app_codename.split('.')
                if codename in get_perms(request.user, request.user.staffprofile):
                    res = True
                    break
        lg.debug("CanViewSelfStaffProfile.has_object_permission with {}: {}".format(request.method, res))
        return res



class CanEditESCPOSWebOperator(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.edit_te_escposweboperator",
        ),
        "PATCH": (
            "taiwan_einvoice.edit_te_escposweboperator",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanEditESCPOSWebOperator.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanEditESCPOSWebOperator.has_object_permission with {}: {}".format(request.method, res))
        return res



class CanOperateESCPOSWebOperator(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.operate_te_escposweb",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanOperateESCPOSWebOperator.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanOperateESCPOSWebOperator.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanOperateESCPOSWebOperator.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj):
                    res = True
                    break
        lg.debug("CanOperateESCPOSWebOperator.has_object_permission with {}: {}".format(request.method, res))
        return res



class CanEditTurnkeyServiceGroup(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.edit_te_turnkeyservicegroup",
        ),
        "retrieve": (
            "taiwan_einvoice.edit_te_turnkeyservicegroup",
        ),
        "partial_update": (
            "taiwan_einvoice.edit_te_turnkeyservicegroup",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = self.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEditTurnkeyServiceGroup.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in self.ACTION_PERMISSION_MAPPING.get(view.action, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj):
                    res = True
                    break
        lg.debug("CanEditTurnkeyServiceGroup.has_object_permission with {}: {}".format(request.method, res))
        return res


class CanEntrySellerInvoiceTrackNo(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.view_te_sellerinvoicetrackno",
        ),
        "retrieve": (
            "taiwan_einvoice.view_te_sellerinvoicetrackno",
        ),
        "upload_csv_to_multiple_create": (
            "taiwan_einvoice.add_te_sellerinvoicetrackno",
        ),
        "destory": (
            "taiwan_einvoice.delete_te_sellerinvoicetrackno",
        ),
        "partial_update": (
            "taiwan_einvoice.add_te_sellerinvoicetrackno",
        ),
        "create_and_upload_blank_numbers": (
            "taiwan_einvoice.delete_te_sellerinvoicetrackno",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanEntrySellerInvoiceTrackNo.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntrySellerInvoiceTrackNo.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanEntrySellerInvoiceTrackNo.ACTION_PERMISSION_MAPPING.get(view.action, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.turnkey_service):
                    res = True
                    break
        lg.debug("CanEntrySellerInvoiceTrackNo.has_object_permission with {}: {}".format(request.method, res))
        return res



class CanEntryEInvoice(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.view_te_einvoice",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanEntryEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntryEInvoice.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanEntryEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.seller_invoice_track_no.turnkey_service):
                    res = True
                    break
        lg.debug("CanEntryEInvoice.has_object_permission with {}: {}".format(request.method, res))
        return res



class CanEntryEInvoicePrintLog(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.view_te_einvoiceprintlog",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanEntryEInvoicePrintLog.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntryEInvoicePrintLog.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanEntryEInvoicePrintLog.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.einvoice.seller_invoice_track_no.turnkey_service):
                    res = True
                    break
        lg.debug("CanEntryEInvoicePrintLog.has_object_permission with {}: {}".format(request.method, res))
        return res



class CanEntryCancelEInvoice(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.view_te_canceleinvoice",
        ),
        "POST": (
            "taiwan_einvoice.add_te_canceleinvoice",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanEntryCancelEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntryCancelEInvoice.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanEntryCancelEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.einvoice.seller_invoice_track_no.turnkey_service):
                    res = True
                    break
        lg.debug("CanEntryCancelEInvoice.has_object_permission with {}: {}".format(request.method, res))
        return res



class CanEntryVoidEInvoice(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.view_te_voideinvoice",
        ),
        "POST": (
            "taiwan_einvoice.add_te_voideinvoice",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanEntryVoidEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntryVoidEInvoice.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanEntryVoidEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.einvoice.seller_invoice_track_no.turnkey_service):
                    res = True
                    break
        lg.debug("CanEntryVoidEInvoice.has_object_permission with {}: {}".format(request.method, res))
        return res



class CanViewLegalEntity(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.view_legalentity",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanViewLegalEntity.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanViewLegalEntity.has_object_permission with {}: {}".format(request.method, res))
        return res



class CanViewTurnkeyService(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.view_turnkeyservice",
        ),
        "retrieve": (
            "taiwan_einvoice.view_turnkeyservice",
        ),
    }




    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanViewTurnkeyService.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanViewTurnkeyService.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanViewTurnkeyService.ACTION_PERMISSION_MAPPING.get(view.action, [])
            for p in permissions:
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj):
                    res = True
                    break
        lg.debug("CanViewTurnkeyService.has_object_permission with {}: {}".format(request.method, res))
        return res


class CanViewBatchEInvoice(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.view_te_alarm_for_programmer",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanViewBatchEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanViewBatchEInvoice.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanViewBatchEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.batch.turnkey_service):
                    res = True
                    break
        lg.debug("CanViewBatchEInvoice.has_object_permission with {}: {}".format(request.method, res))
        return res


class CanViewTEAlarmForProgrammer(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.view_te_alarm_for_programmer",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanViewTEAlarmForProgrammer.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
                return turnkey_services.exists()
        lg.debug("CanViewTEAlarmForProgrammer.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanViewTEAlarmForProgrammer.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.turnkey_service):
                    res = True
                    break
        lg.debug("CanViewTEAlarmForProgrammer.has_object_permission with {}: {}".format(request.method, res))
        return res



class CanViewTEAlarmForGeneralUser(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.view_te_alarm_for_general_user",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanViewTEAlarmForGeneralUser.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
                return TEAlarm.objects.filter(turnkey_service__in=turnkey_services, target_audience_type="g").exists()
        lg.debug("CanViewTEAlarmForGeneralUser.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanViewTEAlarmForGeneralUser.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.turnkey_service):
                    res = True
                    break
        if res and hasattr(self, 'target_audience_type') and "g" != self.target_audience_type:
            res = False
        lg.debug("CanViewTEAlarmForGeneralUser.has_object_permission with {}: {}".format(request.method, res))
        return res



class CanViewSummaryReport(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.view_te_summaryreport",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanViewSummaryReport.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanViewSummaryReport.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanViewSummaryReport.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.turnkey_service):
                    res = True
                    break
        lg.debug("CanViewSummaryReport.has_object_permission with {}: {}".format(request.method, res))
        return res


