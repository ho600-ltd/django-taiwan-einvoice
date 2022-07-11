import logging

from rest_framework.permissions import BasePermission, IsAdminUser



class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_superuser)