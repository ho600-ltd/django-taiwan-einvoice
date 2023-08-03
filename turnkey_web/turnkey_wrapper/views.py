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

from ho600_lib.permissions import FalsePermission, Or
from taiwan_einvoice.turnkey import TurnkeyWebReturnCode
from taiwan_einvoice.paginations import (
    Default30PerPagePagination,
    TenTo1000PerPagePagination,
)


from turnkey_wrapper.permissions import (
    IsSuperUserInLocalhost,
    IsSuperUserInIntranet,
    CounterBasedOTPinRowAndIpCheckForEITurnkeyPermission,
    CounterBasedOTPinRowAndIpCheckForEITurnkeyBatchPermission,
)
from turnkey_wrapper.models import (
    FROM_CONFIG,
    SCHEDULE_CONFIG,
    SIGN_CONFIG,
    TASK_CONFIG,
    TO_CONFIG,
    TURNKEY_MESSAGE_LOG,
    TURNKEY_MESSAGE_LOG_DETAIL,
    TURNKEY_SEQUENCE,
    TURNKEY_SYSEVENT_LOG,
    TURNKEY_TRANSPORT_CONFIG,
    TURNKEY_USER_PROFILE,

    EITurnkey,
    EITurnkeyBatch,
    EITurnkeyBatchEInvoice,
    EITurnkeyDailySummaryResultXML,
    EITurnkeyDailySummaryResult,
    EITurnkeyE0501XML,
    EITurnkeyE0501InvoiceAssignNo,
)
from turnkey_wrapper.serializers import (
    FROM_CONFIGSerializer,
    SCHEDULE_CONFIGSerializer,
    SIGN_CONFIGSerializer,
    TASK_CONFIGSerializer,
    TO_CONFIGSerializer,
    TURNKEY_MESSAGE_LOGSerializer,
    TURNKEY_MESSAGE_LOG_DETAILSerializer,
    TURNKEY_SEQUENCESerializer,
    TURNKEY_SYSEVENT_LOGSerializer,
    TURNKEY_TRANSPORT_CONFIGSerializer,
    TURNKEY_USER_PROFILESerializer,

    EITurnkeySerializer,
    EITurnkeyBatchSerializer,
    EITurnkeyBatchEInvoiceSerializer,
    EITurnkeyDailySummaryResultXMLSerializer,
    EITurnkeyDailySummaryResultSerializer,
    EITurnkeyE0501XMLSerializer,
    EITurnkeyE0501InvoiceAssignNoSerializer,
)
from turnkey_wrapper.filters import (
    FROM_CONFIGFilter,
    SCHEDULE_CONFIGFilter,
    SIGN_CONFIGFilter,
    TASK_CONFIGFilter,
    TO_CONFIGFilter,
    TURNKEY_MESSAGE_LOGFilter,
    TURNKEY_MESSAGE_LOG_DETAILFilter,
    TURNKEY_SEQUENCEFilter,
    TURNKEY_SYSEVENT_LOGFilter,
    TURNKEY_TRANSPORT_CONFIGFilter,
    TURNKEY_USER_PROFILEFilter,

    EITurnkeyFilter,
    EITurnkeyBatchFilter,
    EITurnkeyBatchEInvoiceFilter,
    EITurnkeyDailySummaryResultXMLFilter,
    EITurnkeyDailySummaryResultFilter,
    EITurnkeyE0501XMLFilter,
    EITurnkeyE0501InvoiceAssignNoFilter,
)
from turnkey_wrapper.renderers import (
    PlainFileRenderer,
    XMLFileRenderer,
    TKWBrowsableAPIRenderer,
    FROM_CONFIGHtmlRenderer,
    SCHEDULE_CONFIGHtmlRenderer,
    SIGN_CONFIGHtmlRenderer,
    TASK_CONFIGHtmlRenderer,
    TO_CONFIGHtmlRenderer,
    TURNKEY_MESSAGE_LOGHtmlRenderer,
    TURNKEY_MESSAGE_LOG_DETAILHtmlRenderer,
    TURNKEY_SEQUENCEHtmlRenderer,
    TURNKEY_SYSEVENT_LOGHtmlRenderer,
    TURNKEY_TRANSPORT_CONFIGHtmlRenderer,
    TURNKEY_USER_PROFILEHtmlRenderer,

    EITurnkeyHtmlRenderer,
    EITurnkeyBatchHtmlRenderer,
    EITurnkeyBatchEInvoiceHtmlRenderer,
    EITurnkeyDailySummaryResultXMLHtmlRenderer,
    EITurnkeyDailySummaryResultHtmlRenderer,
    EITurnkeyE0501XMLHtmlRenderer,
    EITurnkeyE0501InvoiceAssignNoHtmlRenderer,
)


@login_required
def index(request, *args, **kwargs):
    return HttpResponseRedirect(reverse("turnkeywrapperapi:eiturnkey-list"))


class FROM_CONFIGModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = FROM_CONFIG.objects.all()
    serializer_class = FROM_CONFIGSerializer
    filter_class = FROM_CONFIGFilter
    renderer_classes = (FROM_CONFIGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )


class SCHEDULE_CONFIGModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = SCHEDULE_CONFIG.objects.all()
    serializer_class = SCHEDULE_CONFIGSerializer
    filter_class = SCHEDULE_CONFIGFilter
    renderer_classes = (SCHEDULE_CONFIGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )


class SIGN_CONFIGModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = SIGN_CONFIG.objects.all()
    serializer_class = SIGN_CONFIGSerializer
    filter_class = SIGN_CONFIGFilter
    renderer_classes = (SIGN_CONFIGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TASK_CONFIGModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = TASK_CONFIG.objects.all()
    serializer_class = TASK_CONFIGSerializer
    filter_class = TASK_CONFIGFilter
    renderer_classes = (TASK_CONFIGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TO_CONFIGModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = TO_CONFIG.objects.all()
    serializer_class = TO_CONFIGSerializer
    filter_class = TO_CONFIGFilter
    renderer_classes = (TO_CONFIGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TURNKEY_MESSAGE_LOGModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = TURNKEY_MESSAGE_LOG.objects.all().order_by('-MESSAGE_DTS', '-SEQNO', '-SUBSEQNO')
    serializer_class = TURNKEY_MESSAGE_LOGSerializer
    filter_class = TURNKEY_MESSAGE_LOGFilter
    renderer_classes = (TURNKEY_MESSAGE_LOGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TURNKEY_MESSAGE_LOG_DETAILModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = TURNKEY_MESSAGE_LOG_DETAIL.objects.all().order_by('-PROCESS_DTS', '-SEQNO', '-SUBSEQNO')
    serializer_class = TURNKEY_MESSAGE_LOG_DETAILSerializer
    filter_class = TURNKEY_MESSAGE_LOG_DETAILFilter
    renderer_classes = (TURNKEY_MESSAGE_LOG_DETAILHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, XMLFileRenderer, PlainFileRenderer)
    http_method_names = ('get', )


    @action(detail=True, methods=['get'])
    def get_file_content(self, request, pk=None):
        SEQNO, SUBSEQNO, TASK = pk.split('-')
        result = TURNKEY_MESSAGE_LOG_DETAIL.objects.get(SEQNO=SEQNO, SUBSEQNO=SUBSEQNO, TASK=TASK)
        try:
            content = open(result.FILENAME, 'r').read()
        except:
            content = _("File Read Error")
        return Response(content)




class TURNKEY_SEQUENCEModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = TURNKEY_SEQUENCE.objects.all()
    serializer_class = TURNKEY_SEQUENCESerializer
    filter_class = TURNKEY_SEQUENCEFilter
    renderer_classes = (TURNKEY_SEQUENCEHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TURNKEY_SYSEVENT_LOGModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = TURNKEY_SYSEVENT_LOG.objects.all().order_by('-EVENTDTS', '-SEQNO', '-SUBSEQNO')
    serializer_class = TURNKEY_SYSEVENT_LOGSerializer
    filter_class = TURNKEY_SYSEVENT_LOGFilter
    renderer_classes = (TURNKEY_SYSEVENT_LOGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TURNKEY_TRANSPORT_CONFIGModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = TURNKEY_TRANSPORT_CONFIG.objects.all()
    serializer_class = TURNKEY_TRANSPORT_CONFIGSerializer
    filter_class = TURNKEY_TRANSPORT_CONFIGFilter
    renderer_classes = (TURNKEY_TRANSPORT_CONFIGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TURNKEY_USER_PROFILEModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = TURNKEY_USER_PROFILE.objects.all()
    serializer_class = TURNKEY_USER_PROFILESerializer
    filter_class = TURNKEY_USER_PROFILEFilter
    renderer_classes = (TURNKEY_USER_PROFILEHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class EITurnkeyModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = EITurnkey.objects.all()
    serializer_class = EITurnkeySerializer
    filter_class = EITurnkeyFilter
    renderer_classes = (EITurnkeyHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', 'post')



    def get_permissions(self):
        if CounterBasedOTPinRowAndIpCheckForEITurnkeyPermission.ACTION_PERMISSION_MAPPING.get(self.action, ()):
            self.permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet, CounterBasedOTPinRowAndIpCheckForEITurnkeyPermission), )
        return super(self.__class__, self).get_permissions()

    

    @action(detail=True, methods=['get'])
    def get_ei_turnkey_summary_results(self, request, pk=None):
        lg = logging.getLogger('turnkey_web')
        eit = EITurnkey.objects.get(id=pk)
        result_date = request.GET.get('result_date', '')
        result_date__gte = request.GET.get('result_date__gte', '')
        if result_date:
            result_date = datetime.datetime.strptime(result_date, "%Y-%m-%d").date()
            eitsrs = eit.eiturnkeydailysummaryresult_set.filter(result_date=result_date).order_by('result_date', 'create_time')[:100]
        elif result_date__gte:
            result_date = datetime.datetime.strptime(result_date__gte, "%Y-%m-%d").date()
            eitsrs = eit.eiturnkeydailysummaryresult_set.filter(result_date__gte=result_date).order_by('result_date')[:100]
        else:
            eitsrs = eit.eiturnkeydailysummaryresult_set.filter().order_by('result_date')[:100]

        result_datas = [{
            "result_date": e.result_date,
            "total_count": e.total_count,
            "good_count": e.good_count,
            "failed_count": e.failed_count,
            "total_batch_einvoice_ids": e.total_batch_einvoice_ids,
            "good_batch_einvoice_ids": e.good_batch_einvoice_ids,
            "failed_batch_einvoice_ids": e.failed_batch_einvoice_ids,
            } for e in eitsrs]
        twrc = TurnkeyWebReturnCode("0")
        result = {
            "return_code": twrc.return_code,
            "return_code_message": twrc.message,
            "results": result_datas,
        }
        return Response(result)
    

    @action(detail=True, methods=['post'])
    def upload_eiturnkey_batch_einvoice_bodys(self, request, pk=None):
        lg = logging.getLogger('turnkey_web')
        eit = EITurnkey.objects.get(id=pk)

        slug = request.data.get('slug', '')
        lg.debug("slug: {}".format(slug))
        parse_bodys = True
        try:
            bodys = json.loads(zlib.decompress(request.data['gz_bodys'].read()))
        except:
            parse_bodys = False
        else:
            if 0 >= len(bodys):
                parse_bodys = False
        lg.debug("bodys count: {}".format(len(bodys)))
        if not parse_bodys:
            twrc = TurnkeyWebReturnCode("002")
            result = {
                "return_code": twrc.return_code,
                "return_code_message": twrc.message,
                "slug": slug,
            }
            return Response(result)

        eit_batch = eit.eiturnkeybatch_set.get(slug=slug)
        result = eit_batch.update_einvoice_bodys(bodys)
        return Response(result)
    

    @action(detail=True, methods=['post'])
    def create_eiturnkey_batch(self, request, pk=None):
        lg = logging.getLogger('turnkey_web')
        eit = EITurnkey.objects.get(id=pk)
        slug = request.data.get('slug', '')
        mig = request.data.get('mig', '')
        lg.debug("EITurnkey: {}".format(eit))
        lg.debug("slug: {}".format(slug))
        lg.debug("mig: {}".format(mig))

        eitb = EITurnkeyBatch(ei_turnkey=eit,
                              slug=slug,
                              mig=mig
                             )
        try:
            eitb.save()
        except Exception as e:
            twrc = TurnkeyWebReturnCode("001")
            result = {
                "return_code": twrc.return_code,
                "return_code_message": twrc.message,
                "message_detail": str(e),
                "ei_turnkey_batch_id": eitb.id,
            }
        else:
            twrc = TurnkeyWebReturnCode("0")
            result = {
                "return_code": twrc.return_code,
                "return_code_message": twrc.message,
                "ei_turnkey_batch_id": eitb.id,
            }
        return Response(result)



class EITurnkeyBatchModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = EITurnkeyBatch.objects.all().order_by('-id')
    serializer_class = EITurnkeyBatchSerializer
    filter_class = EITurnkeyBatchFilter
    renderer_classes = (EITurnkeyBatchHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )


    def get_permissions(self):
        if CounterBasedOTPinRowAndIpCheckForEITurnkeyBatchPermission.ACTION_PERMISSION_MAPPING.get(self.action, ()):
            self.permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet, CounterBasedOTPinRowAndIpCheckForEITurnkeyBatchPermission), )
        return super(self.__class__, self).get_permissions()

    

    @action(detail=True, methods=['get'])
    def get_batch_einvoice_id_status_result_code_set_from_ei_turnkey_batch_einvoices(self, request, pk=None):
        result = EITurnkeyBatch.objects.get(id=pk).get_batch_einvoice_id_status_result_code_set_from_ei_turnkey_batch_einvoices()
        result['return_code'] = "0"
        return Response(result)



class EITurnkeyBatchEInvoiceModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = EITurnkeyBatchEInvoice.objects.all().order_by('-id')
    serializer_class = EITurnkeyBatchEInvoiceSerializer
    filter_class = EITurnkeyBatchEInvoiceFilter
    renderer_classes = (EITurnkeyBatchEInvoiceHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class EITurnkeyDailySummaryResultXMLModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = EITurnkeyDailySummaryResultXML.objects.exclude(is_parsed=True, binary_content=b"").order_by('-result_date', '-id')
    serializer_class = EITurnkeyDailySummaryResultXMLSerializer
    filter_class = EITurnkeyDailySummaryResultXMLFilter
    renderer_classes = (EITurnkeyDailySummaryResultXMLHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, XMLFileRenderer, )
    http_method_names = ('get', )


    @action(detail=True, methods=['get'])
    def get_xml_content(self, request, pk=None):
        result = EITurnkeyDailySummaryResultXML.objects.get(id=pk)
        content = result.content
        return Response(content)



class EITurnkeyDailySummaryResultModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = EITurnkeyDailySummaryResult.objects.all().order_by('-result_date')
    serializer_class = EITurnkeyDailySummaryResultSerializer
    filter_class = EITurnkeyDailySummaryResultFilter
    renderer_classes = (EITurnkeyDailySummaryResultHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class EITurnkeyE0501XMLModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = EITurnkeyE0501XML.objects.exclude(is_parsed=True, binary_content=b"").order_by('-abspath', '-id')
    serializer_class = EITurnkeyE0501XMLSerializer
    filter_class = EITurnkeyE0501XMLFilter
    renderer_classes = (EITurnkeyE0501XMLHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, XMLFileRenderer, )
    http_method_names = ('get', )


    @action(detail=True, methods=['get'])
    def get_xml_content(self, request, pk=None):
        result = EITurnkeyE0501XML.objects.get(id=pk)
        content = result.content
        return Response(content)



class EITurnkeyE0501InvoiceAssignNoModelViewSet(ModelViewSet):
    permission_classes = (Or(IsSuperUserInLocalhost, IsSuperUserInIntranet), )
    pagination_class = TenTo1000PerPagePagination
    queryset = EITurnkeyE0501InvoiceAssignNo.objects.all().order_by('-result_date')
    serializer_class = EITurnkeyE0501InvoiceAssignNoSerializer
    filter_class = EITurnkeyE0501InvoiceAssignNoFilter
    renderer_classes = (EITurnkeyE0501InvoiceAssignNoHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )


