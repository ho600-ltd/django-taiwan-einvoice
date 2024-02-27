import logging

from rest_framework.permissions import BasePermission, IsAdminUser
from guardian.shortcuts import get_objects_for_user, get_perms

from taiwan_einvoice.models import ESCPOSWeb, TEAlarm, TurnkeyService



class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_superuser)



class CanEditTEAStaffProfile(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.view_teastaffprofile",
        ),
        "retrieve": (
            "taiwan_einvoice.view_teastaffprofile",
        ),
        "partial_update": (
            "taiwan_einvoice.change_teastaffprofile",
        ),
        "create": (
            "taiwan_einvoice.add_teastaffprofile",
        )
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for _p in self.ACTION_PERMISSION_MAPPING.get(view.action, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanEditTEAStaffProfile.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for _p in self.ACTION_PERMISSION_MAPPING.get(view.action, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanEditTEAStaffProfile.has_object_permission with {}: {}".format(view.action, res))
        return res



class CanViewSelfTEAStaffProfile(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": "",
        "retrieve": "",
        "partial_update": "",
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active and view.action in self.ACTION_PERMISSION_MAPPING.get(view.action, []):
            res = True
        lg.debug("CanViewSelfTEAStaffProfile.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active and view.action in self.ACTION_PERMISSION_MAPPING.get(view.action, []) and request.user == obj.user:
            res = True
        lg.debug("CanViewSelfTEAStaffProfile.has_object_permission with {}: {}".format(view.action, res))
        return res



class CanEditESCPOSWebOperator(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.edit_te_escposweboperator",
        ),
        "retrieve": (
            "taiwan_einvoice.edit_te_escposweboperator",
        ),
        "partial_update": (
            "taiwan_einvoice.edit_te_escposweboperator",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for _p in self.ACTION_PERMISSION_MAPPING.get(view.action, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanEditESCPOSWebOperator.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for _p in self.ACTION_PERMISSION_MAPPING.get(view.action, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanEditESCPOSWebOperator.has_object_permission with {}: {}".format(view.action, res))
        return res



class CanOperateESCPOSWebOperator(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.operate_te_escposweb",
        ),
        "retrieve": (
            "taiwan_einvoice.operate_te_escposweb",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = CanOperateESCPOSWebOperator.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanOperateESCPOSWebOperator.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for p in CanOperateESCPOSWebOperator.ACTION_PERMISSION_MAPPING.get(view.action, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj):
                    res = True
                    break
        lg.debug("CanOperateESCPOSWebOperator.has_object_permission with {}: {}".format(view.action, res))
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
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = self.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEditTurnkeyServiceGroup.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for p in self.ACTION_PERMISSION_MAPPING.get(view.action, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj):
                    res = True
                    break
        lg.debug("CanEditTurnkeyServiceGroup.has_object_permission with {}: {}".format(view.action, res))
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
        "destroy": (
            "taiwan_einvoice.delete_te_sellerinvoicetrackno",
        ),
        "partial_update": (
            "taiwan_einvoice.add_te_sellerinvoicetrackno",
        ),
        "create_and_upload_blank_numbers": (
            "taiwan_einvoice.delete_te_sellerinvoicetrackno",
        ),
        "ban_to_cancel": (
            "taiwan_einvoice.delete_te_sellerinvoicetrackno",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = CanEntrySellerInvoiceTrackNo.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntrySellerInvoiceTrackNo.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for p in CanEntrySellerInvoiceTrackNo.ACTION_PERMISSION_MAPPING.get(view.action, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.turnkey_service):
                    res = True
                    break
        lg.debug("CanEntrySellerInvoiceTrackNo.has_object_permission with {}: {}".format(view.action, res))
        return res



class CanEntryEInvoice(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.view_te_einvoice",
        ),
        "retrieve": (
            "taiwan_einvoice.view_te_einvoice",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = CanEntryEInvoice.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntryEInvoice.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for p in CanEntryEInvoice.ACTION_PERMISSION_MAPPING.get(view.action, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.seller_invoice_track_no.turnkey_service):
                    res = True
                    break
        lg.debug("CanEntryEInvoice.has_object_permission with {}: {}".format(view.action, res))
        return res



class CanEntryEInvoicePrintLog(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.view_te_einvoiceprintlog",
        ),
        "retrieve": (
            "taiwan_einvoice.view_te_einvoiceprintlog",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = CanEntryEInvoicePrintLog.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntryEInvoicePrintLog.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for p in CanEntryEInvoicePrintLog.ACTION_PERMISSION_MAPPING.get(view.action, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.einvoice.seller_invoice_track_no.turnkey_service):
                    res = True
                    break
        lg.debug("CanEntryEInvoicePrintLog.has_object_permission with {}: {}".format(view.action, res))
        return res



class CanEntryCancelEInvoice(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.view_te_canceleinvoice",
        ),
        "retrieve": (
            "taiwan_einvoice.view_te_canceleinvoice",
        ),
        "create": (
            "taiwan_einvoice.add_te_canceleinvoice",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = CanEntryCancelEInvoice.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntryCancelEInvoice.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for p in CanEntryCancelEInvoice.ACTION_PERMISSION_MAPPING.get(view.action, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.einvoice.seller_invoice_track_no.turnkey_service):
                    res = True
                    break
        lg.debug("CanEntryCancelEInvoice.has_object_permission with {}: {}".format(view.action, res))
        return res



class CanEntryVoidEInvoice(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.view_te_voideinvoice",
        ),
        "retrieve": (
            "taiwan_einvoice.view_te_voideinvoice",
        ),
        "create": (
            "taiwan_einvoice.add_te_voideinvoice",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = CanEntryVoidEInvoice.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntryVoidEInvoice.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for p in CanEntryVoidEInvoice.ACTION_PERMISSION_MAPPING.get(view.action, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.einvoice.seller_invoice_track_no.turnkey_service):
                    res = True
                    break
        lg.debug("CanEntryVoidEInvoice.has_object_permission with {}: {}".format(view.action, res))
        return res



class CanViewLegalEntity(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.view_legalentity",
        ),
        "retrieve": (
            "taiwan_einvoice.view_legalentity",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for _p in self.ACTION_PERMISSION_MAPPING.get(view.action, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanViewLegalEntity.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for _p in self.ACTION_PERMISSION_MAPPING.get(view.action, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanViewLegalEntity.has_object_permission with {}: {}".format(view.action, res))
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
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = CanViewTurnkeyService.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanViewTurnkeyService.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = CanViewTurnkeyService.ACTION_PERMISSION_MAPPING.get(view.action, [])
            for p in permissions:
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj):
                    res = True
                    break
        lg.debug("CanViewTurnkeyService.has_object_permission with {}: {}".format(view.action, res))
        return res


class CanDealWithBatchEInvoice(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.view_te_alarm_for_programmer",
        ),
        "retrieve": (
            "taiwan_einvoice.view_te_alarm_for_programmer",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = CanDealWithBatchEInvoice.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanDealWithBatchEInvoice.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for p in CanDealWithBatchEInvoice.ACTION_PERMISSION_MAPPING.get(view.action, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.batch.turnkey_service):
                    res = True
                    break
        lg.debug("CanDealWithBatchEInvoice.has_object_permission with {}: {}".format(view.action, res))
        return res


class CanViewTEAlarmForProgrammer(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.view_te_alarm_for_programmer",
        ),
        "retrieve": (
            "taiwan_einvoice.view_te_alarm_for_programmer",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = CanViewTEAlarmForProgrammer.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
                return turnkey_services.exists()
        lg.debug("CanViewTEAlarmForProgrammer.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for p in CanViewTEAlarmForProgrammer.ACTION_PERMISSION_MAPPING.get(view.action, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.turnkey_service):
                    res = True
                    break
        lg.debug("CanViewTEAlarmForProgrammer.has_object_permission with {}: {}".format(view.action, res))
        return res



class CanViewTEAlarmForGeneralUser(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.view_te_alarm_for_general_user",
        ),
        "retrieve": (
            "taiwan_einvoice.view_te_alarm_for_general_user",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = CanViewTEAlarmForGeneralUser.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                turnkey_services = get_objects_for_user(request.user, permissions, any_perm=True)
                return TEAlarm.objects.filter(turnkey_service__in=turnkey_services, target_audience_type="g").exists()
        lg.debug("CanViewTEAlarmForGeneralUser.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for p in CanViewTEAlarmForGeneralUser.ACTION_PERMISSION_MAPPING.get(view.action, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.turnkey_service):
                    res = True
                    break
        if res and hasattr(self, 'target_audience_type') and "g" != self.target_audience_type:
            res = False
        lg.debug("CanViewTEAlarmForGeneralUser.has_object_permission with {}: {}".format(view.action, res))
        return res



class CanViewSummaryReport(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "list": (
            "taiwan_einvoice.view_te_summaryreport",
        ),
        "retrieve": (
            "taiwan_einvoice.view_te_summaryreport",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = CanViewSummaryReport.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanViewSummaryReport.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            for p in CanViewSummaryReport.ACTION_PERMISSION_MAPPING.get(view.action, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.turnkey_service):
                    res = True
                    break
        lg.debug("CanViewSummaryReport.has_object_permission with {}: {}".format(view.action, res))
        return res



class CanViewE0501InvoiceAssignNo(BasePermission):
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
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = CanViewE0501InvoiceAssignNo.ACTION_PERMISSION_MAPPING.get(view.action, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanViewE0501InvoiceAssignNo.has_permission with {}: {}".format(view.action, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('taiwan_einvoice')
        res = False
        if request.user.is_authenticated and hasattr(request.user, 'teastaffprofile') and request.user.teastaffprofile.is_active:
            permissions = CanViewE0501InvoiceAssignNo.ACTION_PERMISSION_MAPPING.get(view.action, [])
            ts = TurnkeyService.objects.filter(seller__legalentity__identifier=obj.identifier)
            for p in permissions:
                app, codename = p.split('.')
                for t_obj in ts:
                    if codename in get_perms(request.user, t_obj):
                        res = True
                        break
        lg.debug("CanViewE0501InvoiceAssignNo.has_object_permission with {}: {}".format(view.action, res))
        return res

