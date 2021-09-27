import datetime
import logging
import pytz

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from rest_framework.serializers import PrimaryKeyRelatedField, HyperlinkedIdentityField, ModelSerializer, Serializer
from taiwan_einvoice.models import ESCPOSWeb



class ESCPOSWebSerializer(ModelSerializer):

    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:escposweb-detail", lookup_field='pk')

    class Meta:
        model = ESCPOSWeb
        fields = '__all__'



    def get_queryset(self):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_superuser:
            return ESCPOSWeb.objects.all().order_by('-id')
        else:
            return ESCPOSWeb.objects.none()