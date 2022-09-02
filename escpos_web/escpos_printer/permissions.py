import logging

from rest_framework.permissions import IsAdminUser



class IsSuperUserInIntranet(IsAdminUser):
    def has_permission(self, request, view):
        return True
        if bool(request.user and request.user.is_superuser):
            remote_addr = request.META['REMOTE_ADDR']
            if remote_addr.startswith("10.") or remote_addr.startswith("192.168."):
                pass
            elif remote_addr.startswith("172.") and remote_addr.split('.')[1] in [str(i) for i in range(16, 32)]:
                pass
            else:
                return False
            return True
        return False


    def has_object_permission(self, request, view, obj):
        return True
        if bool(request.user and request.user.is_superuser):
            remote_addr = request.META['REMOTE_ADDR']
            if remote_addr.startswith("10.") or remote_addr.startswith("192.168."):
                pass
            elif remote_addr.startswith("172.") and remote_addr.split('.')[1] in [str(i) for i in range(16, 32)]:
                pass
            else:
                return False
            return True
        return False