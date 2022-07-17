import logging

from rest_framework.permissions import BasePermission, IsAdminUser



class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_superuser)



class CounterBasedOTPinRowForEITurnkeyPermission(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "retrieve": (True, ),
    }


    def has_permission(self, request, view):
        if request.headers.get('x-counter-based-otp-in-row', '') and self.ACTION_PERMISSION_MAPPING.get(view.action, ()):
            return True
        else:
            return False


    def has_object_permission(self, request, view, obj):
        if request.headers.get('x-counter-based-otp-in-row', ''):
            otps = request.headers['x-counter-based-otp-in-row']
        else:
            return False
        result = obj.verify_counter_based_otp_in_row(otps.split(','))
        if result:
            lg = logging.getLogger('turnkey_web')
            lg.debug("CounterBasedOTPinRowForEITurnkeyPermission:\n\notps: {}\nverify_otps: {}".format(otps, result))
            return True
        else:
            return False