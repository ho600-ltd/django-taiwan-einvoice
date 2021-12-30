import datetime
import logging
import pytz

from django.conf import settings
from django.contrib.auth.models import User, Permission, AnonymousUser 
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import utc, now
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from rest_framework.serializers import CharField, IntegerField, BooleanField
from rest_framework.serializers import PrimaryKeyRelatedField, HyperlinkedIdentityField, ModelSerializer, Serializer, ReadOnlyField, ChoiceField
from rest_framework.serializers import ValidationError
from guardian.shortcuts import get_objects_for_user, assign_perm, get_perms
from taiwan_einvoice.models import (
    NotEnoughNumberError,
    ESCPOSWeb,
    Printer,
    LegalEntity,
    Seller,
    TurnkeyWeb,
    SellerInvoiceTrackNo,
    EInvoice,
    EInvoicePrintLog,
    CancelEInvoice,
)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'last_name', 'first_name', 'email', 'username',
        )



class ESCPOSWebSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:escposweb-detail", lookup_field='pk')
    mask_hash_key = CharField(read_only=True)



    class Meta:
        model = ESCPOSWeb
        fields = (
            'id', 'resource_uri', 'mask_hash_key', 'name', 'slug', 'hash_key',
        )
        extra_kwargs = {
            'hash_key': {'write_only': True},
        }



    def get_queryset(self):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_superuser:
            return ESCPOSWeb.objects.all().order_by('-id')
        else:
            return ESCPOSWeb.objects.none()



class PrinterSerializer(ModelSerializer):
    escpos_web_dict = ESCPOSWebSerializer(source='escpos_web', read_only=True)



    class Meta:
        model = Printer
        fields = '__all__'



class LegalEntitySerializerForUser(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:legalentity-detail", lookup_field='pk')
    identifier = ReadOnlyField()

    class Meta:
        model = LegalEntity
        fields = '__all__'



    def get_queryset(self):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_superuser:
            return LegalEntity.objects.all().order_by('-id')
        else:
            return LegalEntity.objects.none()



class LegalEntitySerializerForSuperUser(LegalEntitySerializerForUser):
    identifier = CharField()



class SellerSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:seller-detail", lookup_field='pk')
    legal_entity_dict = LegalEntitySerializerForUser(source='legal_entity', read_only=True)

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
    seller_dict = SellerSerializer(source='seller', read_only=True)
    count_now_use_07_sellerinvoicetrackno_blank_no = IntegerField(read_only=True)
    count_now_use_08_sellerinvoicetrackno_blank_no = IntegerField(read_only=True)
    mask_hash_key = CharField(read_only=True)
    mask_qrcode_seed = CharField(read_only=True)
    mask_turnkey_seed = CharField(read_only=True)
    mask_download_seed = CharField(read_only=True)
    mask_epl_base_set = CharField(read_only=True)



    class Meta:
        model = TurnkeyWeb
        fields = (
            'id', 'resource_uri', 'seller_dict',
            'count_now_use_07_sellerinvoicetrackno_blank_no',
            'count_now_use_08_sellerinvoicetrackno_blank_no',
            'on_working',
            'name',
            'hash_key',
            'mask_hash_key',
            'transport_id',
            'party_id',
            'routing_id',
            'mask_qrcode_seed',
            'mask_turnkey_seed',
            'mask_download_seed',
            'mask_epl_base_set',
            'qrcode_seed',
            'turnkey_seed',
            'download_seed',
            'epl_base_set',
            'note',
            'seller'
        )
        extra_kwargs = {
            'hash_key': {'write_only': True},
            'qrcode_seed': {'write_only': True},
            'turnkey_seed': {'write_only': True},
            'download_seed': {'write_only': True},
            'epl_base_set': {'write_only': True},
        }


    def get_queryset(self):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_superuser:
            return TurnkeyWeb.objects.all().order_by('-id')
        else:
            return TurnkeyWeb.objects.none()



class TurnkeyWebRelatedField(PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        return get_objects_for_user(request.user if request else AnonymousUser,
                                    ("taiwan_einvoice.add_te_sellerinvoicetrackno",
                                    ),
                                    any_perm=True,
                                    with_superuser=True,
                                    accept_global_perms=False,
                                    ).order_by('id')



class SellerInvoiceTrackNoSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:sellerinvoicetrackno-detail", lookup_field='pk')
    turnkey_web = TurnkeyWebRelatedField(required=True, allow_null=False)
    turnkey_web_dict = TurnkeyWebSerializer(source='turnkey_web', read_only=True)
    type = ChoiceField(choices=SellerInvoiceTrackNo.type_choices)
    type__display = CharField(read_only=True)
    count_blank_no = IntegerField(read_only=True)
    year_month_range = CharField(read_only=True)

    class Meta:
        model = SellerInvoiceTrackNo
        fields = '__all__'



    def get_queryset(self):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_superuser:
            return SellerInvoiceTrackNo.objects.all().order_by('-id')
        else:
            return SellerInvoiceTrackNo.objects.none()


class DetailsContentField(ReadOnlyField):
    def get_attribute(self, instance):
        request = self.context['request']
        if request.GET.get('with_details_content', '') in ['true', '1']:
            return super(DetailsContentField, self).get_attribute(instance)
        return []


class EInvoiceSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:einvoice-detail", lookup_field='pk')
    creator_dict = UserSerializer(source='creator', read_only=True)
    seller_invoice_track_no_dict = SellerInvoiceTrackNoSerializer(source='seller_invoice_track_no', read_only=True)
    track_no = CharField(read_only=True)
    track_no_ = CharField(read_only=True)
    donate_mark = CharField(read_only=True)
    carrier_type__display = CharField(read_only=True)
    details_content = DetailsContentField()
    amount_is_warning = BooleanField(read_only=True)
    is_canceled = BooleanField(read_only=True)

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
    user_dict = UserSerializer(source='user', read_only=True)
    printer_dict = PrinterSerializer(source='printer', read_only=True)
    einvoice_dict = EInvoiceSerializer(source='einvoice', read_only=True)

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
    creator_dict = UserSerializer(source='creator', read_only=True)
    einvoice_dict = EInvoiceSerializer(source='einvoice', read_only=True)
    new_einvoice_dict = EInvoiceSerializer(source='new_einvoice', read_only=True)



    class Meta:
        model = CancelEInvoice
        fields = '__all__'



    def get_queryset(self):
        request = self.context.get('request', None)
        if request and request.user and request.user.is_superuser:
            return CancelEInvoice.objects.all().order_by('-id')
        else:
            return CancelEInvoice.objects.none()