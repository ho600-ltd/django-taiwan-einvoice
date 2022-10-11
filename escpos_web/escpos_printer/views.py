#!/usr/bin/env python
from http.client import HTTPResponse
import logging, json, zlib, datetime
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from libs import get_boot_seed, get_public_ip

from escpos_printer.permissions import IsInIntranet
from escpos_printer.serializers import PrinterSerializer, TEAWebSerializer
from escpos_printer.renderers import EPWBrowsableAPIRenderer, PrinterHtmlRenderer, TEAWebHtmlRenderer, OutgoingIPHtmlRenderer
from escpos_printer.models import Printer, TEAWeb

from taiwan_einvoice.paginations import (
    Default30PerPagePagination,
    TenTo1000PerPagePagination,
)

from escpos_printer.filters import (
    PrinterFilter,
    TEAWebFilter,
)


@login_required
def index(request, *args, **kwargs):
    return HttpResponseRedirect(reverse("escposwebapi:printer-list"))


class PrinterModelViewSet(ModelViewSet):
    permission_classes = (IsInIntranet, IsAuthenticated, )
    pagination_class = TenTo1000PerPagePagination
    queryset = Printer.objects.all().order_by('-id')
    serializer_class = PrinterSerializer
    filter_class = PrinterFilter
    renderer_classes = (PrinterHtmlRenderer, EPWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TEAWebModelViewSet(ModelViewSet):
    permission_classes = (IsInIntranet, IsAuthenticated, )
    pagination_class = Default30PerPagePagination
    queryset = TEAWeb.objects.all().order_by('-id')
    serializer_class = TEAWebSerializer
    filter_class = TEAWebFilter
    renderer_classes = (TEAWebHtmlRenderer, EPWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', 'patch', )



    def update(self, request, *args, **kwargs):
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        pass_key = data.get('pass_key', '')
        if not pass_key or pass_key != get_boot_seed():
            er = {
                "error_title": _("Pass Key Error"),
                "error_message": _("Pass Key is not '{}'!").format(pass_key),
            }
            return Response(er, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)



class OutgoingIPViewSet(ViewSet):
    permission_classes = (IsInIntranet, IsAuthenticated, )
    renderer_classes = (OutgoingIPHtmlRenderer, EPWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )


    def list(self, request):
        try:
            outgoing_ip = get_public_ip()
        except:
            outgoing_ip = '?.?.?.?'

        data = {
            "results": [{
                "outgoing_ip": outgoing_ip,
            }],
        }
        return Response(data)