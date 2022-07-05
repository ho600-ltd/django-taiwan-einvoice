import logging

from rest_framework.permissions import BasePermission, IsAdminUser
from guardian.shortcuts import get_objects_for_user, get_perms

from taiwan_einvoice.models import ESCPOSWeb



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
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanEditStaffProfile.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
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
        lg = logging.getLogger('info')
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
        lg = logging.getLogger('info')
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
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanEditESCPOSWebOperator.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
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
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanOperateESCPOSWebOperator.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanOperateESCPOSWebOperator.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
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
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.edit_te_turnkeyservicegroup",
        ),
        "PATCH": (
            "taiwan_einvoice.edit_te_turnkeyservicegroup",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanEditTurnkeyServiceGroup.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanEditTurnkeyServiceGroup.has_object_permission with {}: {}".format(request.method, res))
        return res


class CanEntrySellerInvoiceTrackNo(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.view_te_sellerinvoicetrackno",
        ),
        "POST": (
            "taiwan_einvoice.add_te_sellerinvoicetrackno",
        ),
        "DELETE": (
            "taiwan_einvoice.delete_te_sellerinvoicetrackno",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanEntrySellerInvoiceTrackNo.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntrySellerInvoiceTrackNo.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanEntrySellerInvoiceTrackNo.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.turnkey_web):
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
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanEntryEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntryEInvoice.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanEntryEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.seller_invoice_track_no.turnkey_web):
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
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanEntryEInvoicePrintLog.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntryEInvoicePrintLog.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanEntryEInvoicePrintLog.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.einvoice.seller_invoice_track_no.turnkey_web):
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
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanEntryCancelEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntryCancelEInvoice.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanEntryCancelEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.einvoice.seller_invoice_track_no.turnkey_web):
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
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanEntryVoidEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanEntryVoidEInvoice.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanEntryVoidEInvoice.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.einvoice.seller_invoice_track_no.turnkey_web):
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
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanViewLegalEntity.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanViewLegalEntity.has_object_permission with {}: {}".format(request.method, res))
        return res



class CanViewTurnkeyService(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.view_turnkeyservice",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            permissions = CanViewTurnkeyService.METHOD_PERMISSION_MAPPING.get(request.method, [])
            if permissions:
                res = get_objects_for_user(request.user, permissions, any_perm=True).exists()
        lg.debug("CanViewTurnkeyService.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
        res = False
        if request.user.is_authenticated and request.user.staffprofile and request.user.staffprofile.is_active:
            for p in CanViewTurnkeyService.METHOD_PERMISSION_MAPPING.get(request.method, []):
                app, codename = p.split('.')
                if codename in get_perms(request.user, obj.einvoice.seller_invoice_track_no.turnkey_web):
                    res = True
                    break
        lg.debug("CanViewTurnkeyService.has_object_permission with {}: {}".format(request.method, res))
        return res

