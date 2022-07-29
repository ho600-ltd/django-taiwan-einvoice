import logging

from rest_framework.permissions import BasePermission, IsAdminUser



class IsSuperUserInLocalhost(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser and '127.0.0.1' == request.META['REMOTE_ADDR'])


    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_superuser and '127.0.0.1' == request.META['REMOTE_ADDR'])



class CounterBasedOTPinRowForEITurnkeyPermission(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "retrieve": (True, ),
        "create_eiturnkey_batch": (True, ),
        "upload_eiturnkey_batch_einvoice_bodys": (True, ),
    }


    def has_permission(self, request, view):
        if request.headers.get('X-COUNTER-BASED-OTP-IN-ROW', '') and self.ACTION_PERMISSION_MAPPING.get(view.action, ()):
            return True
        else:
            return False


    def has_object_permission(self, request, view, obj):
        if request.headers.get('X-COUNTER-BASED-OTP-IN-ROW', ''):
            otps = request.headers['X-COUNTER-BASED-OTP-IN-ROW']
        else:
            return False
        result = obj.verify_counter_based_otp_in_row(otps.split(','))
        if result:
            lg = logging.getLogger('turnkey_web')
            lg.debug("CounterBasedOTPinRowForEITurnkeyPermission:\n\notps: {}\nverify_otps: {}".format(otps, result))
            return True
        else:
            return False



class CounterBasedOTPinRowForEITurnkeyBatchPermission(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "get_batch_einvoice_id_status_result_code_set_from_ei_turnkey_batch_einvoices": (True, ),
    }


    def has_permission(self, request, view):
        if request.headers.get('X-COUNTER-BASED-OTP-IN-ROW', '') and self.ACTION_PERMISSION_MAPPING.get(view.action, ()):
            return True
        else:
            return False


    def has_object_permission(self, request, view, obj):
        if request.headers.get('X-COUNTER-BASED-OTP-IN-ROW', ''):
            otps = request.headers['X-COUNTER-BASED-OTP-IN-ROW']
        else:
            return False
        result = obj.ei_turnkey.verify_counter_based_otp_in_row(otps.split(','))
        if result:
            lg = logging.getLogger('turnkey_web')
            lg.debug("CounterBasedOTPinRowForEITurnkeyBatchPermission:\n\notps: {}\nverify_otps: {}".format(otps, result))
            return True
        else:
            return False