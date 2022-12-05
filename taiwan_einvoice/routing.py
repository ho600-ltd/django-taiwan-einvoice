# taiwan_einvoice/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/taiwan_einvoice/escpos_web/(?P<escpos_web_id>\d+)/(?P<token_auth>[\w-]+)/$', consumers.ESCPOSWebConsumer.as_asgi()),
    re_path(r'ws/taiwan_einvoice/escpos_web/(?P<escpos_web_id>\d+)/status/(?P<token_auth>[\w-]+)/$', consumers.ESCPOSWebStatusConsumer.as_asgi()),
    re_path(r'ws/taiwan_einvoice/escpos_web/(?P<escpos_web_id>\d+)/print_result/(?P<token_auth>[\w-]+)/$', consumers.ESCPOSWebPrintResultConsumer.as_asgi()),
]