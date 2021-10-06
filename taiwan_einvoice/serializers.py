import datetime
import logging
import pytz

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from rest_framework.serializers import CharField, IntegerField
from rest_framework.serializers import PrimaryKeyRelatedField, HyperlinkedIdentityField, ModelSerializer, Serializer
from taiwan_einvoice.models import (
    ESCPOSWeb,
    LegalEntity,
    Seller,
    TurnkeyWeb,
    SellerInvoiceTrackNo,
    EInvoice,
    EInvoicePrintLog,
    CancelEInvoice,
)



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



class LegalEntitySerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:legalentity-detail", lookup_field='pk')

    class Meta:
        model = LegalEntity
        fields = '__all__'



    def get_queryset(self):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_superuser:
            return ESCPOSWeb.objects.all().order_by('-id')
        else:
            return ESCPOSWeb.objects.none()



class SellerSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:seller-detail", lookup_field='pk')

    class Meta:
        model = Seller
        fields = '__all__'



    def get_queryset(self):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_superuser:
            return Seller.objects.all().order_by('-id')
        else:
            return Seller.objects.none()



class TurnkeyWebSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:turnkeyweb-detail", lookup_field='pk')

    class Meta:
        model = TurnkeyWeb
        fields = '__all__'



    def get_queryset(self):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_superuser:
            return TurnkeyWeb.objects.all().order_by('-id')
        else:
            return TurnkeyWeb.objects.none()



class SellerInvoiceTrackNoSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:sellerinvoicetrackno-detail", lookup_field='pk')
    type__display = CharField(read_only=True)
    count_blank_no = IntegerField(read_only=True)

    class Meta:
        model = SellerInvoiceTrackNo
        fields = '__all__'



    def get_queryset(self):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_superuser:
            return SellerInvoiceTrackNo.objects.all().order_by('-id')
        else:
            return SellerInvoiceTrackNo.objects.none()



class EInvoiceSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:einvoice-detail", lookup_field='pk')

    class Meta:
        model = EInvoice
        fields = '__all__'



    def get_queryset(self):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_superuser:
            return EInvoice.objects.all().order_by('-id')
        else:
            return EInvoice.objects.none()



class EInvoicePrintLogSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:einvoiceprintlog-detail", lookup_field='pk')

    class Meta:
        model = EInvoicePrintLog
        fields = '__all__'



    def get_queryset(self):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_superuser:
            return EInvoicePrintLog.objects.all().order_by('-id')
        else:
            return EInvoicePrintlog.objects.none()



class CancelEInvoiceSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:canceleinvoice-detail", lookup_field='pk')

    class Meta:
        model = CancelEInvoice
        fields = '__all__'



    def get_queryset(self):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_superuser:
            return CancelEInvoice.objects.all().order_by('-id')
        else:
            return CancelEInvoice.objects.none()