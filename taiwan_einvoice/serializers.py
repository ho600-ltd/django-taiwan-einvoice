import datetime
import logging
import pytz

from django.conf import settings
from django.contrib.auth.models import User, Group, Permission, AnonymousUser 
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import utc, now
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from rest_framework.serializers import CharField, IntegerField, BooleanField, DateTimeField, JSONField
from rest_framework.serializers import (
    PrimaryKeyRelatedField,
    HyperlinkedIdentityField,
    ModelSerializer,
    Serializer,
    ReadOnlyField,
    ChoiceField,
    RelatedField,
)
from rest_framework.serializers import ValidationError, SerializerMethodField
from rest_framework.exceptions import PermissionDenied
from guardian.shortcuts import get_objects_for_user, assign_perm, get_perms
from taiwan_einvoice.models import (
    NotEnoughNumberError,
    EInvoiceMIG,
    StaffProfile,
    ESCPOSWeb,
    Printer,
    LegalEntity,
    Seller,
    TurnkeyService,
    SellerInvoiceTrackNo,
    EInvoice,
    EInvoicePrintLog,
    CancelEInvoice,
    VoidEInvoice,
    UploadBatch,
    BatchEInvoice,
    AuditType,
    AuditLog,
)


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'last_name', 'first_name', 'email', 'username',
        )


class EInvoiceMIGSerializer(ModelSerializer):
    class Meta:
        model = EInvoiceMIG
        fields = '__all__'


class StaffProfileSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:staffprofile-detail", lookup_field='pk')
    user_dict = UserSerializer(source='user', read_only=True)
    in_printer_admin_group = BooleanField()
    in_manager_group = BooleanField()
    groups = JSONField(read_only=True)
    count_within_groups = JSONField(read_only=True)


    class Meta:
        model = StaffProfile
        fields = '__all__'



    def update(self, instance, validated_data):
        if self.context['request'].user == instance.user:
            raise PermissionDenied(detail=_("You can not edit yourself"))
        group_dict = {
            "in_printer_admin_group": Group.objects.get(name='TaiwanEInvoicePrinterAdminGroup'),
            "in_manager_group": Group.objects.get(name='TaiwanEInvoiceManagerGroup')
        }
        for key in ['in_printer_admin_group', 'in_manager_group']:
            if key in validated_data:
                if validated_data[key]:
                    instance.user.groups.add(group_dict[key])
                else:
                    instance.user.groups.remove(group_dict[key])
                del validated_data[key]
        return super().update(instance, validated_data)


    def create(self, validated_data):
        data = {
            "in_printer_admin_group": validated_data['in_printer_admin_group'],
            "in_manager_group": validated_data['in_manager_group'],
        }
        for key in ['in_printer_admin_group', 'in_manager_group']:
            del validated_data[key]
        instance = super().create(validated_data)
        for key, group in {"in_printer_admin_group": Group.objects.get(name='TaiwanEInvoicePrinterAdminGroup'),
                           "in_manager_group": Group.objects.get(name='TaiwanEInvoiceManagerGroup')}.items():
            if key in data:
                if data[key]:
                    instance.user.groups.add(group)
                else:
                    instance.user.groups.remove(group)
        return instance



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



class ESCPOSWebOperatorSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:escposweboperator-detail", lookup_field='pk')
    admins = StaffProfileSerializer(read_only=True, many=True)
    operators = StaffProfileSerializer(read_only=True, many=True)



    class Meta:
        model = ESCPOSWeb
        fields = (
            'id', 'resource_uri', 'name', 'slug', 'admins', 'operators',
        )



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



class LegalEntitySerializerForSuperUser(LegalEntitySerializerForUser):
    identifier = CharField()



class SellerSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:seller-detail", lookup_field='pk')
    legal_entity_dict = LegalEntitySerializerForUser(source='legal_entity', read_only=True)

    class Meta:
        model = Seller
        fields = '__all__'



class TurnkeyServiceSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:turnkeyservice-detail", lookup_field='pk')
    seller_dict = SellerSerializer(source='seller', read_only=True)
    count_now_use_07_sellerinvoicetrackno_blank_no = IntegerField(read_only=True)
    count_now_use_08_sellerinvoicetrackno_blank_no = IntegerField(read_only=True)
    mask_hash_key = CharField(read_only=True)
    mask_qrcode_seed = CharField(read_only=True)
    mask_turnkey_seed = CharField(read_only=True)
    mask_download_seed = CharField(read_only=True)
    mask_epl_base_set = CharField(read_only=True)
    upload_cronjob_format__display = CharField(read_only=True)



    class Meta:
        model = TurnkeyService
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
            'auto_upload_c0401_einvoice',
            'upload_cronjob_format__display',
            'tkw_endpoint',
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



class StaffGroupSerializer(ModelSerializer):
    display_name = SerializerMethodField()
    staffs = SerializerMethodField()


    class Meta:
        model = Group
        fields = (
            'id', 'name', 'display_name', 'staffs',
        )



    def get_display_name(self, instance):
        return ''.join(instance.name.split(':')[2:])


    def get_staffs(self, instance):
        request = self.context['request']
        users = instance.user_set.all()
        return StaffProfileSerializer(StaffProfile.objects.filter(user__in=users).order_by('nickname'),
                                      many=True,
                                      context={'request': request}).data



class TurnkeyServiceGroupSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:turnkeyservicegroup-detail", lookup_field='pk')
    groups = StaffGroupSerializer(read_only=True, many=True)
    groups_count = SerializerMethodField()
    groups_permissions = JSONField()



    class Meta:
        model = TurnkeyService
        fields = (
            'id', 'resource_uri', 'name', 'groups', 'groups_count', 'groups_permissions',
        )
        extra_kwargs = {
        }
    

    def get_groups_count(self, instance):
        return len(instance.groups)



class TurnkeyServiceRelatedField(PrimaryKeyRelatedField):
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
    turnkey_web = TurnkeyServiceRelatedField(required=True, allow_null=False)
    turnkey_web_dict = TurnkeyServiceSerializer(source='turnkey_web', read_only=True)
    type = ChoiceField(choices=SellerInvoiceTrackNo.type_choices)
    type__display = CharField(read_only=True)
    count_blank_no = IntegerField(read_only=True)
    year_month_range = CharField(read_only=True)
    can_be_deleted = BooleanField(read_only=True)

    class Meta:
        model = SellerInvoiceTrackNo
        fields = '__all__'



class DetailsContentField(ReadOnlyField):
    def get_attribute(self, instance):
        request = self.context['request']
        if request.GET.get('with_details_content', '') in ['true', '1']:
            return super(DetailsContentField, self).get_attribute(instance)
        return []



class EInvoiceSimpleSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:einvoice-detail", lookup_field='pk')
    track_no = CharField(read_only=True)
    track_no_ = CharField(read_only=True)


    class Meta:
        model = EInvoice
        fields = ['resource_uri', 'id', 'track_no_', 'track_no', ]



class EInvoiceSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:einvoice-detail", lookup_field='pk')
    str_name = SerializerMethodField()
    creator_dict = UserSerializer(source='creator', read_only=True)
    seller_invoice_track_no_dict = SellerInvoiceTrackNoSerializer(source='seller_invoice_track_no', read_only=True)
    track_no = CharField(read_only=True)
    track_no_ = CharField(read_only=True)
    donate_mark = CharField(read_only=True)
    carrier_type__display = CharField(read_only=True)
    details_content = DetailsContentField()
    amount_is_warning = BooleanField(read_only=True)
    buyer_is_business_entity = BooleanField(read_only=True)
    is_canceled = BooleanField(read_only=True)
    is_voided = BooleanField(read_only=True)
    can_void = BooleanField(read_only=True)
    canceled_time = DateTimeField(read_only=True)
    related_einvoices = EInvoiceSimpleSerializer(read_only=True, many=True)



    class Meta:
        model = EInvoice
        fields = '__all__'

    

    def get_str_name(self, instance):
        return str(instance)



class EInvoicePrintLogSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:einvoiceprintlog-detail", lookup_field='pk')
    user_dict = UserSerializer(source='user', read_only=True)
    printer_dict = PrinterSerializer(source='printer', read_only=True)
    einvoice_dict = EInvoiceSerializer(source='einvoice', read_only=True)

    class Meta:
        model = EInvoicePrintLog
        fields = '__all__'



class CancelEInvoiceSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:canceleinvoice-detail", lookup_field='pk')
    str_name = SerializerMethodField()
    creator_dict = UserSerializer(source='creator', read_only=True)
    einvoice_dict = EInvoiceSerializer(source='einvoice', read_only=True)
    new_einvoice_dict = EInvoiceSerializer(source='new_einvoice', read_only=True)



    class Meta:
        model = CancelEInvoice
        fields = '__all__'



    def get_str_name(self, instance):
        return str(instance)



class VoidEInvoiceSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:voideinvoice-detail", lookup_field='pk')
    str_name = SerializerMethodField()
    creator_dict = UserSerializer(source='creator', read_only=True)
    einvoice_dict = EInvoiceSerializer(source='einvoice', read_only=True)
    new_einvoice_dict = EInvoiceSerializer(source='new_einvoice', read_only=True)



    class Meta:
        model = VoidEInvoice
        fields = '__all__'



    def get_str_name(self, instance):
        return str(instance)


class UploadBatchSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:uploadbatch-detail", lookup_field='pk')
    str_name = SerializerMethodField()
    mig_type_dict = EInvoiceMIGSerializer(source="mig_type", read_only=True)
    batch_einvoice_count = IntegerField(read_only=True)
    turnkey_service_dict = TurnkeyServiceSerializer(source="turnkey_service", read_only=True)
    get_kind_display = CharField(read_only=True)
    get_status_display = CharField(read_only=True)



    class Meta:
        model = UploadBatch
        fields = '__all__'



    def get_str_name(self, instance):
        return str(instance)



class BatchEInvoiceSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:batcheinvoice-detail", lookup_field='pk')
    batch_dict = UploadBatchSerializer(source="batch", read_only=True)
    year_month_range = CharField(read_only=True)
    content_object_dict = SerializerMethodField()



    class Meta:
        model = BatchEInvoice
        fields = '__all__'

    

    def get_content_object_dict(self, instance):
        request = self.context.get('request', None)
        return {
            "einvoice": EInvoiceSerializer(instance.content_object, context={"request": request}),
            "canceleinvoice": CancelEInvoiceSerializer(instance.content_object, context={"request": request}),
            "voideinvoice": VoidEInvoiceSerializer(instance.content_object, context={"request": request}),
        }[instance.content_type.model].data




class AuditTypeSerializer(ModelSerializer):
    class Meta:
        model = AuditType
        fields = '__all__'



class AuditLogSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="taiwan_einvoice:taiwaneinvoiceapi:auditlog-detail", lookup_field='pk')
    creator_dict = UserSerializer(source='creator', read_only=True)
    type_dict = AuditTypeSerializer(source='type', read_only=True)
    turnkey_service_dict = TurnkeyServiceSerializer(source='turnkey_service', read_only=True)
    content_object_dict = SerializerMethodField()



    class Meta:
        model = AuditLog
        fields = '__all__'



    def get_content_object_dict(self, instance):
        request = self.context.get('request', None)
        return {
            "uploadbatch": UploadBatchSerializer(instance.content_object, context={"request": request})
        }[instance.content_type.model].data