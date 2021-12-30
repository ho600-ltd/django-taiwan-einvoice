import logging

from rest_framework.permissions import BasePermission, IsAdminUser
from guardian.shortcuts import get_user_perms, get_objects_for_user

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
