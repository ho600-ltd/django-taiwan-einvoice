import logging

from rest_framework.permissions import BasePermission, IsAdminUser
from guardian.shortcuts import get_user_perms, get_objects_for_user

from taiwan_einvoice.models import ESCPOSWeb



class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

