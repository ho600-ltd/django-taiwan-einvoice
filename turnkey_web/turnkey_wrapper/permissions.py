import logging

from rest_framework.permissions import BasePermission, IsAdminUser
from turnkey_wrapper.models import EITurnkey



class IsSuperUserInLocalhost(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser and '127.0.0.1' == request.META['REMOTE_ADDR'])


    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_superuser and '127.0.0.1' == request.META['REMOTE_ADDR'])



class IsSuperUserInIntranet(IsAdminUser):
    def has_permission(self, request, view):
        if bool(request.user and request.user.is_superuser):
            remote_addr = request.META['REMOTE_ADDR']
            if remote_addr.startswith("10.") or remote_addr.startswith("192.168."):
                return True
            elif remote_addr.startswith("172.") and remote_addr.split('.')[1] in [str(i) for i in range(16, 32)]:
                return True
        return False


    def has_object_permission(self, request, view, obj):
        remote_addr = request.META['REMOTE_ADDR']
        if bool(request.user and request.user.is_superuser):
            if remote_addr.startswith("10.") or remote_addr.startswith("192.168."):
                pass
            elif remote_addr.startswith("172.") and remote_addr.split('.')[1] in [str(i) for i in range(16, 32)]:
                pass
            else:
                return False
            model_name = obj._meta.model_name
            if "EITurnkey".lower() == model_name:
                allow_ips = obj.allow_ips
            elif "EITurnkeyBatchEInvoice".lower() == model_name:
                allow_ips = obj.ei_turnkey_batch.ei_turnkey.allow_ips
            elif model_name in ["EITurnkeyBatch".lower(), "EITurnkeyDailySummaryResultXML".lower(), "EITurnkeyDailySummaryResult".lower(), ]:
                allow_ips = obj.ei_turnkey.allow_ips
            else:
                allow_ips = []
                for eit in EITurnkey.objects.filter(can_sync_to_ei=True):
                    allow_ips.extend(eit.allow_ips)
            if [] == allow_ips or remote_addr in allow_ips:
                return True
        return False



class CounterBasedOTPinRowAndIpCheckForEITurnkeyPermission(BasePermission):
    ACTION_PERMISSION_MAPPING = {
        "retrieve": (True, ),
        "create_eiturnkey_batch": (True, ),
        "upload_eiturnkey_batch_einvoice_bodys": (True, ),
        "get_ei_turnkey_summary_results": (True, ),
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
        if result and (not obj.allow_ips or request.META['REMOTE_ADDR'] in obj.allow_ips):
            lg = logging.getLogger('turnkey_web')
            lg.debug("CounterBasedOTPinRowForEITurnkeyPermission:\n\notps: {}\nverify_otps: {}".format(otps, result))
            return True
        else:
            return False



class CounterBasedOTPinRowAndIpCheckForEITurnkeyBatchPermission(BasePermission):
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
        if result and (not obj.allow_ips or request.META['REMOTE_ADDR'] in obj.allow_ips):
            lg = logging.getLogger('turnkey_web')
            lg.debug("CounterBasedOTPinRowForEITurnkeyBatchPermission:\n\notps: {}\nverify_otps: {}".format(otps, result))
            return True
        else:
            return False