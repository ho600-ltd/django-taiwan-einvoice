from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet


from turnkey_wrapper.permissions import IsSuperUser
from turnkey_wrapper.models import (
    FROM_CONFIG,
    TASK_CONFIG,
)
from turnkey_wrapper.serializers import (
    FROM_CONFIGSerializer,
    TASK_CONFIGSerializer,
)
from turnkey_wrapper.filters import (
    FROM_CONFIGFilter,
    TASK_CONFIGFilter,
)
from turnkey_wrapper.renderers import (
    TKWBrowsableAPIRenderer,
    FROM_CONFIGHtmlRenderer,
    TASK_CONFIGHtmlRenderer,
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



class TASK_CONFIGModelViewSet(ModelViewSet):
    permission_classes = (IsSuperUser, )
    pagination_class = TenTo1000PerPagePagination
    queryset = TASK_CONFIG.objects.all()
    serializer_class = TASK_CONFIGSerializer
    filter_class = TASK_CONFIGFilter
    renderer_classes = (TASK_CONFIGHtmlRenderer, TKWBrowsableAPIRenderer, JSONRenderer, )
    http_method_names = ('get', )