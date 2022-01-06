import logging

from rest_framework.permissions import BasePermission, IsAdminUser
from guardian.shortcuts import get_objects_for_user, get_perms

from taiwan_einvoice.models import ESCPOSWeb



class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class CanOperateStaffProfile(BasePermission):
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
            for _p in self.METHOD_PERMISSION_MAPPING[request.method]:
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanOperateStaffProfile.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
        res = False
        if request.user.staffprofile and request.user.staffprofile.is_active:
            for _p in self.METHOD_PERMISSION_MAPPING[request.method]:
                res = request.user.has_perm(_p)
                if res:
                    break
        lg.debug("CanOperateStaffProfile.has_object_permission with {}: {}".format(request.method, res))
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
            for app_codename in self.METHOD_PERMISSION_MAPPING[request.method]:
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
            for app_codename in self.METHOD_PERMISSION_MAPPING[request.method]:
                app, codename = app_codename.split('.')
                if codename in get_perms(request.user, request.user.staffprofile):
                    res = True
                    break
        lg.debug("CanViewSelfStaffProfile.has_object_permission with {}: {}".format(request.method, res))
        return res

class CanViewESCPOSWeb(BasePermission):
    METHOD_PERMISSION_MAPPING = {
        "GET": (
            "taiwan_einvoice.view_escposweb",
            "taiwan_einvoice.operate_te_escposweb",
        ),
    }


    def has_permission(self, request, view):
        lg = logging.getLogger('info')
        res = False
        for _p in self.METHOD_PERMISSION_MAPPING[request.method]:
            res = request.user.has_perm(_p)
            if res:
                break
        if not res:
            objs = get_objects_for_user(request.user,
                                        self.METHOD_PERMISSION_MAPPING[request.method],
                                        any_perm=True)
            if objs:
                res = True
        lg.debug("CanViewESCPOSWeb.has_permission with {}: {}".format(request.method, res))
        return res
        

    def has_object_permission(self, request, view, obj):
        lg = logging.getLogger('info')
        res = False
        for _p in self.METHOD_PERMISSION_MAPPING[request.method]:
            res = request.user.has_perm(_p)
            if res:
                break
        if not res:
            for p in get_perms(request.user, obj):
                if p in self.METHOD_PERMISSION_MAPPING[request.method]:
                    res = True
                    break
        lg.debug("CanViewSelfStaffProfile.has_object_permission with {}: {}".format(request.method, res))
        return res
