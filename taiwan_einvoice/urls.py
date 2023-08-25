# taiwan_einvoice/urls.py
import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, Http404
from django.urls import include, path, re_path
from django.utils.translation import gettext as _
from django.views.static import serve
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONRenderer
from rest_framework.schemas import get_schema_view
from taiwan_einvoice.renderers import TEBrowsableAPIRenderer

from . import views


def check_permissions(my_function):
    def inner_function(*args, **kw):
        R = args[0]
        if R.user and R.user.is_authenticated:
            if hasattr(settings, "TAIWAN_EINVOICE_MANUAL_ROOT") and os.path.isdir(os.path.join(settings.TAIWAN_EINVOICE_MANUAL_ROOT, 'taiwan_einvoice_manual_html')):
                kw['document_root'] = os.path.join(settings.TAIWAN_EINVOICE_MANUAL_ROOT, 'taiwan_einvoice_manual_html')
            elif hasattr(settings, "ROOT") and os.path.isdir(os.path.join(settings.ROOT, 'taiwan_einvoice_manual_html')):
                kw['document_root'] = os.path.join(settings.ROOT, 'taiwan_einvoice_manual_html')
            elif os.path.isdir(os.path.join(os.path.dirname(__file__), 'taiwan_einvoice_manual_html')):
                kw['document_root'] = os.path.join(os.path.dirname(__file__), 'taiwan_einvoice_manual_html')
            else:
                kw['document_root'] = 'NOT_EXIST'
            if not kw.get('path', ''):
                kw['path'] = 'index.html'
            http_404_true = False
            try:
                response = my_function(*args, **kw)
            except Http404:
                http_404_true = True
            if http_404_true or isinstance(response, HttpResponseNotFound):
                return HttpResponse(_("No Permission or Page does not ready"))
            else:
                return my_function(*args, **kw)
        else:
            return HttpResponseRedirect(settings.SOCIAL_AUTH_LOGIN_REDIRECT_URL)
    return inner_function



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
router.register('teastaffprofile', views.TEAStaffProfileModelViewSet, basename="teastaffprofile")
router.register('escposweb', views.ESCPOSWebModelViewSet, basename="escposweb")
router.register('escposweboperator', views.ESCPOSWebOperatorModelViewSet, basename="escposweboperator")
router.register('legalentity', views.LegalEntityModelViewSet, basename="legalentity")
router.register('seller', views.SellerModelViewSet, basename="seller")
router.register('turnkeyservice', views.TurnkeyServiceModelViewSet, basename="turnkeyservice")
router.register('turnkeyservicegroup', views.TurnkeyServiceGroupModelViewSet, basename="turnkeyservicegroup")
router.register('sellerinvoicetrackno', views.SellerInvoiceTrackNoModelViewSet, basename="sellerinvoicetrackno")
router.register('einvoice', views.EInvoiceModelViewSet, basename="einvoice")
router.register('einvoiceprintlog', views.EInvoicePrintLogModelViewSet, basename="einvoiceprintlog")
router.register('canceleinvoice', views.CancelEInvoiceModelViewSet, basename="canceleinvoice")
router.register('voideinvoice', views.VoidEInvoiceModelViewSet, basename="voideinvoice")
router.register('uploadbatch', views.UploadBatchModelViewSet, basename="uploadbatch")
router.register('batcheinvoice', views.BatchEInvoiceModelViewSet, basename="batcheinvoice")
router.register('auditlog', views.AuditLogModelViewSet, basename="auditlog")
router.register('summaryreport', views.SummaryReportModelViewSet, basename="summaryreport")
router.register('tealarm', views.TEAlarmModelViewSet, basename="tealarm")
router.register('e0501invoiceassignno', views.E0501InvoiceAssignNoModelViewSet, basename="e0501invoiceassignno")

app_name = 'taiwan_einvoice'
urlpatterns = [
    path('escpos_web_demo/<int:escpos_web_id>/', views.escpos_web_demo, name='escpos_web_demo'),
    re_path(r'^api/{}/'.format(TaiwanEInvoiceAPIRootView.version),
        include((router.urls, "taiwaneinvoiceapi"), namespace="taiwaneinvoiceapi")),
    re_path(r'^manual/(?P<path>.*)', check_permissions(serve), name='taiwan_einvoice_manual_html'),
    path('', views.index, name='index'),
]