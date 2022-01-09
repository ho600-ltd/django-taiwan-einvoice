import logging

from rest_framework.permissions import BasePermission, IsAdminUser
from guardian.shortcuts import get_objects_for_user, get_perms

from taiwan_einvoice.models import ESCPOSWeb



class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
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
        if request.user.staffprofile and request.user.staffprofile.is_active:
            for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanEditStaffProfile.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
        res = False
        if request.user.staffprofile and request.user.staffprofile.is_active:
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
        if request.user.staffprofile:
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
        if request.user.staffprofile:
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
        for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
            res = request.user.has_perm(_p)
            if res:
                break
        lg.debug("CanEditESCPOSWebOperator.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
        res = False
        for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
            res = request.user.has_perm(_p)
            if res:
                break
        lg.debug("CanEditESCPOSWebOperator.has_object_permission with {}: {}".format(request.method, res))
        return res



class CanEditTurnkeyWebGroup(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.edit_te_turnkeywebgroup",
        ),
        "PATCH": (
            "taiwan_einvoice.edit_te_turnkeywebgroup",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('info')
        res = False
        for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
            res = request.user.has_perm(_p)
            if res:
                break
        lg.debug("CanEditTurnkeyWebGroup.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
        res = False
        for _p in self.METHOD_PERMISSION_MAPPING.get(request.method, []):
            res = request.user.has_perm(_p)
            if res:
                break
        lg.debug("CanEditTurnkeyWebGroup.has_object_permission with {}: {}".format(request.method, res))
        return res

