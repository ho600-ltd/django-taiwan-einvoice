from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from turnkey_wrapper.permissions import IsSuperUser
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
)
from turnkey_wrapper.renderers import (
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
)



class TenTo1000PerPagePagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 10
    max_page_size = 1000



class FROM_CONFIGModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    pagination_class = TenTo1000PerPagePagination
    queryset = FROM_CONFIG.objects.all()
    serializer_class = FROM_CONFIGSerializer
    filter_class = FROM_CONFIGFilter
    renderer_classes = (FROM_CONFIGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )


class SCHEDULE_CONFIGModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    pagination_class = TenTo1000PerPagePagination
    queryset = SCHEDULE_CONFIG.objects.all()
    serializer_class = SCHEDULE_CONFIGSerializer
    filter_class = SCHEDULE_CONFIGFilter
    renderer_classes = (SCHEDULE_CONFIGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )


class SIGN_CONFIGModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    pagination_class = TenTo1000PerPagePagination
    queryset = SIGN_CONFIG.objects.all()
    serializer_class = SIGN_CONFIGSerializer
    filter_class = SIGN_CONFIGFilter
    renderer_classes = (SIGN_CONFIGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TASK_CONFIGModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    pagination_class = TenTo1000PerPagePagination
    queryset = TASK_CONFIG.objects.all()
    serializer_class = TASK_CONFIGSerializer
    filter_class = TASK_CONFIGFilter
    renderer_classes = (TASK_CONFIGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TO_CONFIGModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    pagination_class = TenTo1000PerPagePagination
    queryset = TO_CONFIG.objects.all()
    serializer_class = TO_CONFIGSerializer
    filter_class = TO_CONFIGFilter
    renderer_classes = (TO_CONFIGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TURNKEY_MESSAGE_LOGModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    pagination_class = TenTo1000PerPagePagination
    queryset = TURNKEY_MESSAGE_LOG.objects.all()
    serializer_class = TURNKEY_MESSAGE_LOGSerializer
    filter_class = TURNKEY_MESSAGE_LOGFilter
    renderer_classes = (TURNKEY_MESSAGE_LOGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TURNKEY_MESSAGE_LOG_DETAILModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    pagination_class = TenTo1000PerPagePagination
    queryset = TURNKEY_MESSAGE_LOG_DETAIL.objects.all()
    serializer_class = TURNKEY_MESSAGE_LOG_DETAILSerializer
    filter_class = TURNKEY_MESSAGE_LOG_DETAILFilter
    renderer_classes = (TURNKEY_MESSAGE_LOG_DETAILHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TURNKEY_SEQUENCEModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    pagination_class = TenTo1000PerPagePagination
    queryset = TURNKEY_SEQUENCE.objects.all()
    serializer_class = TURNKEY_SEQUENCESerializer
    filter_class = TURNKEY_SEQUENCEFilter
    renderer_classes = (TURNKEY_SEQUENCEHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TURNKEY_SYSEVENT_LOGModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    pagination_class = TenTo1000PerPagePagination
    queryset = TURNKEY_SYSEVENT_LOG.objects.all()
    serializer_class = TURNKEY_SYSEVENT_LOGSerializer
    filter_class = TURNKEY_SYSEVENT_LOGFilter
    renderer_classes = (TURNKEY_SYSEVENT_LOGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TURNKEY_TRANSPORT_CONFIGModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    pagination_class = TenTo1000PerPagePagination
    queryset = TURNKEY_TRANSPORT_CONFIG.objects.all()
    serializer_class = TURNKEY_TRANSPORT_CONFIGSerializer
    filter_class = TURNKEY_TRANSPORT_CONFIGFilter
    renderer_classes = (TURNKEY_TRANSPORT_CONFIGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )



class TURNKEY_USER_PROFILEModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    pagination_class = TenTo1000PerPagePagination
    queryset = TURNKEY_USER_PROFILE.objects.all()
    serializer_class = TURNKEY_USER_PROFILESerializer
    filter_class = TURNKEY_USER_PROFILEFilter
    renderer_classes = (TURNKEY_USER_PROFILEHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )