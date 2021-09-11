# taiwan_einvoice/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/taiwan_einvoice/escpos_web/(?P<escpos_web_id>\d+)/$', consumers.ESCPOSWebConsumer.as_asgi()),
]