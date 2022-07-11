# turnkey_web/urls.py

from django.contrib import admin
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from rest_framework.renderers import JSONRenderer
from rest_framework.schemas import get_schema_view
from turnkey_wrapper.renderers import TKWBrowsableAPIRenderer

from turnkey_wrapper import views

class TurnkeyWrapperAPIRootView(routers.APIRootView):
    """ Endpoints of Turnkey Wrapper Api
    """
    version = 'v1'
    renderer_classes = (JSONRenderer, )


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
router.register('TASK_CONFIG', views.TASK_CONFIGModelViewSet, basename="taskconfig")

app_name = 'turnkey_web'
urlpatterns = [
    path('__admin__/', admin.site.urls),
    re_path(r'^api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^api/{}/'.format(TurnkeyWrapperAPIRootView.version),
        include((router.urls, "turnkeywrapperapi"), namespace="turnkeywrapperapi")),
    path('i18n/', include('django.conf.urls.i18n'), name='i18n'),
    path('jsi18n.js', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]