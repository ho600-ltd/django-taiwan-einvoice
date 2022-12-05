from asgiref.sync import async_to_sync
from django.contrib.auth import user_logged_out
from django.dispatch import receiver
from django.utils.translation import gettext as _
from channels.layers import get_channel_layer
from taiwan_einvoice.models import UserConnectESCPOSWebLog


@receiver(user_logged_out)
def on_user_logout(sender, request, user, **kwargs):
    channel_layer = get_channel_layer()
    if user:
        for ucel in user.userconnectescposweblog_set.filter(is_connected=True):
            group_name = "escpos_web_status_{}".format(ucel.escpos_web.id)
            error_message_dict = {
                    'type': 'show_error_message',
                    'error_message': {"error_message": {"value": _("Already Logout")}},
                }
            async_to_sync(channel_layer.group_send)(
                group_name,
                error_message_dict
            )
            async_to_sync(channel_layer.group_discard)(
                group_name,
                ucel.channel_name
            )
            ucel.is_connected = False
            ucel.save()