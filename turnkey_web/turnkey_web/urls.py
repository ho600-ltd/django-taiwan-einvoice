# turnkey_web/urls.py

from django.contrib import admin
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog
from django.views.static import serve
from django.conf import settings
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONRenderer
from rest_framework.schemas import get_schema_view
from turnkey_wrapper import permissions
from turnkey_wrapper.renderers import TKWBrowsableAPIRenderer
from turnkey_wrapper.permissions import IsSuperUserInLocalhost

from turnkey_wrapper import views

class TurnkeyWrapperAPIRootView(routers.APIRootView):
    """ Endpoints of Turnkey Wrapper Api
    """
    version = 'v1'
    renderer_classes = (JSONRenderer, )
    permission_classes = (IsSuperUserInLocalhost, )


    def initial(self, request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            self.renderer_classes = (TKWBrowsableAPIRenderer, JSONRenderer, )
        super().initial(request, *args, **kwargs)



class TurnkeyWrapperRouter(routers.DefaultRouter):
    """ The **Class Name**(TurnkeyWrapperAPIRootView) will be
        the "page-header name" in the "Browseble Api Root Page"
        and
        The __doc__ of TurnkeyWrapperAPIRootView class will be
        the description in the "Browseble Api Root Page"
    """
    APIRootView = TurnkeyWrapperAPIRootView


router = TurnkeyWrapperRouter()
router.register('FROM_CONFIG', views.FROM_CONFIGModelViewSet, basename="fromconfig")
router.register('SCHEDULE_CONFIG', views.SCHEDULE_CONFIGModelViewSet, basename="scheduleconfig")
router.register('SIGN_CONFIG', views.SIGN_CONFIGModelViewSet, basename="signconfig")
router.register('TASK_CONFIG', views.TASK_CONFIGModelViewSet, basename="taskconfig")
router.register('TO_CONFIG', views.TO_CONFIGModelViewSet, basename="toconfig")
router.register('TURNKEY_MESSAGE_LOG', views.TURNKEY_MESSAGE_LOGModelViewSet, basename="turnkeymessagelog")
router.register('TURNKEY_MESSAGE_LOG_DETAIL', views.TURNKEY_MESSAGE_LOG_DETAILModelViewSet, basename="turnkeymessagelogdetail")
router.register('TURNKEY_SEQUENCE', views.TURNKEY_SEQUENCEModelViewSet, basename="turnkeysequence")
router.register('TURNKEY_SYSEVENT_LOG', views.TURNKEY_SYSEVENT_LOGModelViewSet, basename="turnkeysyseventlog")
router.register('TURNKEY_TRANSPORT_CONFIG', views.TURNKEY_TRANSPORT_CONFIGModelViewSet, basename="turnkeytransportconfig")
router.register('TURNKEY_USER_PROFILE', views.TURNKEY_USER_PROFILEModelViewSet, basename="turnkeyuserprofile")

router.register('EITurnkey', views.EITurnkeyModelViewSet, basename="eiturnkey")
router.register('EITurnkeyBatch', views.EITurnkeyBatchModelViewSet, basename="eiturnkeybatch")
router.register('EITurnkeyBatchEInvoice', views.EITurnkeyBatchEInvoiceModelViewSet, basename="eiturnkeybatcheinvoice")
router.register('EITurnkeyDailySummaryResultXML', views.EITurnkeyDailySummaryResultXMLModelViewSet, basename="eiturnkeydailysummaryresultxml")
router.register('EITurnkeyDailySummaryResult', views.EITurnkeyDailySummaryResultModelViewSet, basename="eiturnkeydailysummaryresult")

app_name = 'turnkey_web'
urlpatterns = [
    path('__admin__/', admin.site.urls),
    re_path(r'^api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^api/{}/'.format(TurnkeyWrapperAPIRootView.version),
        include((router.urls, "turnkeywrapperapi"), namespace="turnkeywrapperapi")),
    path('crontab_monitor/', include('crontab_monitor.urls'), name='crontab_monitor'),
    path('i18n/', include('django.conf.urls.i18n'), name='i18n'),
    path('jsi18n.js', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    re_path(r'^statics/(.*)', serve,
        {'document_root': settings.STATIC_ROOT}, name='statics'),
]
