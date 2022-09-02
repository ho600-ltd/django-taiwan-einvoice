"""escpos_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog
from django.views.static import serve
from django.conf import settings
from rest_framework import routers
from rest_framework.renderers import JSONRenderer
from rest_framework.schemas import get_schema_view
from escpos_printer.renderers import EPWBrowsableAPIRenderer
from escpos_printer.permissions import IsSuperUserInIntranet

from escpos_printer import views



class ESCPOSWebAPIRootView(routers.APIRootView):
    """ Endpoints of ESCPOS Web Api
    """
    version = 'v1'
    renderer_classes = (JSONRenderer, )
    permission_classes = (IsSuperUserInIntranet, )


    def initial(self, request, *args, **kwargs):
        if request.user.is_staff or request.user.is_superuser:
            self.renderer_classes = (EPWBrowsableAPIRenderer, JSONRenderer, )
        super().initial(request, *args, **kwargs)



class ESCPOSWebRouter(routers.DefaultRouter):
    """ The **Class Name**(ESCPOSWebAPIRootView) will be
        the "page-header name" in the "Browseble Api Root Page"
        and
        The __doc__ of ESCPOSWebAPIRootView class will be
        the description in the "Browseble Api Root Page"
    """
    APIRootView = ESCPOSWebAPIRootView


router = ESCPOSWebRouter()
router.register('Printer', views.PrinterModelViewSet, basename="printer")
router.register('TEAWeb', views.TEAWebModelViewSet, basename="teaweb")


# def login(request, *args, **kwargs):
#     from django.urls import reverse 
#     from django.http import HttpResponseRedirect
#     return HttpResponseRedirect(reverse("rest_framework:login"))


app_name = 'escpos_web'
urlpatterns = [
    re_path('^admin/password_change/$', views.index, name='index'),
    path('admin/', admin.site.urls),
    re_path(r'^api/api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^api/{}/'.format(ESCPOSWebAPIRootView.version),
        include((router.urls, "ESCPOSWebapi"), namespace="escposwebapi")),
    path('i18n/', include('django.conf.urls.i18n'), name='i18n'),
    path('jsi18n.js', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    re_path(r'^statics/(.*)', serve, {'document_root': settings.STATIC_ROOT}, name='statics'),
    path('', views.index, name='index'),
]