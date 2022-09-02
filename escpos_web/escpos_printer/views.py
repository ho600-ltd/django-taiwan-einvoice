#!/usr/bin/env python
from http.client import HTTPResponse
import logging, json, zlib, datetime
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from escpos_printer.permissions import IsSuperUserInIntranet
from escpos_printer.serializers import PrinterSerializer, TEAWebSerializer
from escpos_printer.renderers import EPWBrowsableAPIRenderer, PrinterHtmlRenderer, TEAWebHtmlRenderer
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
    permission_classes = (IsSuperUserInIntranet, )
    pagination_class = TenTo1000PerPagePagination
    queryset = Printer.objects.all()
    serializer_class = PrinterSerializer
    filter_class = PrinterFilter
    renderer_classes = (PrinterHtmlRenderer, EPWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TEAWebModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUserInIntranet, )
    pagination_class = Default30PerPagePagination
    queryset = TEAWeb.objects.all()
    serializer_class = TEAWebSerializer
    filter_class = TEAWebFilter
    renderer_classes = (TEAWebHtmlRenderer, EPWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', 'patch')



    # @action(detail=True, methods=['get'])
    # def get_ei_turnkey_summary_results(self, request, pk=None):
    #     lg = logging.getLogger('turnkey_web')
    #     eit = Printer.objects.get(id=pk)
    #     result_date__gte = request.GET.get('result_date__gte', '')
    #     if result_date__gte:
    #         result_date = datetime.datetime.strptime(result_date__gte, "%Y-%m-%d").date()
    #         eitsrs = eit.Printerdailysummaryresult_set.filter(result_date__gte=result_date).order_by('result_date')[:100]
    #     else:
    #         eitsrs = eit.Printerdailysummaryresult_set.filter().order_by('result_date')[:100]

    #     result_datas = [{
    #         "result_date": e.result_date,
    #         "total_count": e.total_count,
    #         "good_count": e.good_count,
    #         "failed_count": e.failed_count,
    #         "total_batch_einvoice_ids": e.total_batch_einvoice_ids,
    #         "good_batch_einvoice_ids": e.good_batch_einvoice_ids,
    #         "failed_batch_einvoice_ids": e.failed_batch_einvoice_ids,
    #         } for e in eitsrs]
    #     twrc = TurnkeyWebReturnCode("0")
    #     result = {
    #         "return_code": twrc.return_code,
    #         "return_code_message": twrc.message,
    #         "results": result_datas,
    #     }
    #     return Response(result)
    

    # @action(detail=True, methods=['post'])
    # def upload_Printer_batch_einvoice_bodys(self, request, pk=None):
    #     lg = logging.getLogger('turnkey_web')
    #     eit = Printer.objects.get(id=pk)

    #     slug = request.data.get('slug', '')
    #     lg.debug("slug: {}".format(slug))
    #     parse_bodys = True
    #     try:
    #         bodys = json.loads(zlib.decompress(request.data['gz_bodys'].read()))
    #     except:
    #         parse_bodys = False
    #     else:
    #         if 0 >= len(bodys):
    #             parse_bodys = False
    #     lg.debug("bodys count: {}".format(len(bodys)))
    #     if not parse_bodys:
    #         twrc = TurnkeyWebReturnCode("002")
    #         result = {
    #             "return_code": twrc.return_code,
    #             "return_code_message": twrc.message,
    #             "slug": slug,
    #         }
    #         return Response(result)

    #     eit_batch = eit.Printerbatch_set.get(slug=slug)
    #     result = eit_batch.update_einvoice_bodys(bodys)
    #     return Response(result)
    

    # @action(detail=True, methods=['post'])
    # def create_Printer_batch(self, request, pk=None):
        # lg = logging.getLogger('turnkey_web')
        # eit = Printer.objects.get(id=pk)
        # slug = request.data.get('slug', '')
        # mig = request.data.get('mig', '')
        # lg.debug("Printer: {}".format(eit))
        # lg.debug("slug: {}".format(slug))
        # lg.debug("mig: {}".format(mig))

        # eitb = PrinterBatch(ei_turnkey=eit,
        #                       slug=slug,
        #                       mig=mig
        #                      )
        # try:
        #     eitb.save()
        # except Exception as e:
        #     twrc = TurnkeyWebReturnCode("001")
        #     result = {
        #         "return_code": twrc.return_code,
        #         "return_code_message": twrc.message,
        #         "message_detail": str(e),
        #         "ei_turnkey_batch_id": eitb.id,
        #     }
        # else:
        #     twrc = TurnkeyWebReturnCode("0")
        #     result = {
        #         "return_code": twrc.return_code,
        #         "return_code_message": twrc.message,
        #         "ei_turnkey_batch_id": eitb.id,
        #     }
        # return Response(result)

