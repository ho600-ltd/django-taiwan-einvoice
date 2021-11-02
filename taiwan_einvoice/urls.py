# taiwan_einvoice/urls.py
from django.urls import include, path, re_path
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONRenderer
from rest_framework.schemas import get_schema_view
from taiwan_einvoice.renderers import TEBrowsableAPIRenderer

from . import views

class TaiwanEInvoiceAPIRootView(routers.APIRootView):
    """ Endpoints of Taiwan EInvoice Api
    """
    version = 'v1'
    renderer_classes = (JSONRenderer, )


    def initial(self, request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            self.renderer_classes = (TEBrowsableAPIRenderer, JSONRenderer, )
        super().initial(request, *args, **kwargs)



class TaiwanEInvoiceRouter(routers.DefaultRouter):
    """ The **Class Name**(TaiwanEInvoiceAPIRootView) will be
        the "page-header name" in the "Browseble Api Root Page"
        and
        The __doc__ of TaiwanEInvoiceAPIRootView class will be
        the description in the "Browseble Api Root Page"
    """
    APIRootView = TaiwanEInvoiceAPIRootView


router = TaiwanEInvoiceRouter()
router.register('escposweb', views.ESCPOSWebModelViewSet, basename="escposweb")
router.register('legalentity', views.LegalEntityModelViewSet, basename="legalentity")
router.register('seller', views.SellerModelViewSet, basename="seller")
router.register('turnkeyweb', views.TurnkeyWebModelViewSet, basename="turnkeyweb")
router.register('sellerinvoicetrackno', views.SellerInvoiceTrackNoModelViewSet, basename="sellerinvoicetrackno")
router.register('einvoice', views.EInvoiceModelViewSet, basename="einvoice")
router.register('einvoiceprintlog', views.EInvoicePrintLogModelViewSet, basename="einvoiceprintlog")
router.register('canceleinvoice', views.CancelEInvoiceModelViewSet, basename="canceleinvoice")

app_name = 'taiwan_einvoice'
urlpatterns = [
    path('escpos_web_demo/<int:escpos_web_id>/', views.escpos_web_demo, name='escpos_web_demo'),
    re_path(r'^api/{}/'.format(TaiwanEInvoiceAPIRootView.version),
        include((router.urls, "taiwaneinvoiceapi"), namespace="taiwaneinvoiceapi")),
    path('', views.index, name='index'),
]