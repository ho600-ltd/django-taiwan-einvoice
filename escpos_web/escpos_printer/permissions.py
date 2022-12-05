import logging

from rest_framework.permissions import BasePermission



class IsInIntranet(BasePermission):
    def has_permission(self, request, view):
        in_intranet = False
        remote_addr = request.META['REMOTE_ADDR']
        if remote_addr.startswith("10.") or remote_addr.startswith("192.168."):
            in_intranet = True
        elif remote_addr.startswith("172.") and remote_addr.split('.')[1] in [str(i) for i in range(16, 32)]:
            in_intranet = True
        return in_intranet


    def has_object_permission(self, request, view, obj):
        in_intranet = False
        remote_addr = request.META['REMOTE_ADDR']
        if remote_addr.startswith("10.") or remote_addr.startswith("192.168."):
            in_intranet = True
        elif remote_addr.startswith("172.") and remote_addr.split('.')[1] in [str(i) for i in range(16, 32)]:
            in_intranet = True
        return in_intranet