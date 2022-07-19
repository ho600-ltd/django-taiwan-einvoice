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
from turnkey_wrapper.models import (
    FROM_CONFIG,
    SCHEDULE_CONFIG,
    SIGN_CONFIG,
    TASK_CONFIG,
    TO_CONFIG,
    TURNKEY_MESSAGE_LOG,
    TURNKEY_MESSAGE_LOG_DETAIL,
    TURNKEY_SEQUENCE,
    TURNKEY_SYSEVENT_LOG,
    TURNKEY_TRANSPORT_CONFIG,
    TURNKEY_USER_PROFILE,

    EITurnkey,
    EITurnkeyBatch,
    EITurnkeyBatchEInvoice,
)


class FROM_CONFIGSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:fromconfig-detail")

    class Meta:
        model = FROM_CONFIG
        fields = '__all__'



class SCHEDULE_CONFIGSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:scheduleconfig-detail")
    


    class Meta:
        model = SCHEDULE_CONFIG
        fields = '__all__'



class SIGN_CONFIGSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:taskconfig-detail")
    


    class Meta:
        model = SIGN_CONFIG
        fields = '__all__'



class TASK_CONFIGSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:taskconfig-detail")
    


    class Meta:
        model = TASK_CONFIG
        fields = '__all__'



class TO_CONFIGSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:taskconfig-detail")
    


    class Meta:
        model = TO_CONFIG
        fields = '__all__'



class TURNKEY_MESSAGE_LOGSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:taskconfig-detail")
    


    class Meta:
        model = TURNKEY_MESSAGE_LOG
        fields = '__all__'



class TURNKEY_MESSAGE_LOG_DETAILSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:taskconfig-detail")
    


    class Meta:
        model = TURNKEY_MESSAGE_LOG_DETAIL
        fields = '__all__'



class TURNKEY_SEQUENCESerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:taskconfig-detail")
    


    class Meta:
        model = TURNKEY_SEQUENCE
        fields = '__all__'



class TURNKEY_SYSEVENT_LOGSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:taskconfig-detail")
    


    class Meta:
        model = TURNKEY_SYSEVENT_LOG
        fields = '__all__'



class TURNKEY_TRANSPORT_CONFIGSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:taskconfig-detail")
    


    class Meta:
        model = TURNKEY_TRANSPORT_CONFIG
        fields = '__all__'



class TURNKEY_USER_PROFILESerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:taskconfig-detail")
    


    class Meta:
        model = TURNKEY_USER_PROFILE
        fields = '__all__'



class EITurnkeySerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:eiturnkey-detail")
    mask_hash_key = CharField(read_only=True)
    


    class Meta:
        model = EITurnkey
        fields = [
            "id",
            "resource_uri",
            "execute_abspath",
            "data_abspath",
            "mask_hash_key",
            "transport_id",
            "party_id",
            "routing_id",
            "tea_turnkey_service_endpoint",
            "allow_ips",
            "endpoint",
        ]



class EITurnkeyBatchSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:eiturnkeybatch-detail")
    ei_turnkey_dict = EITurnkeySerializer(read_only=True, source="ei_turnkey")
    count = IntegerField(read_only=True)
    


    class Meta:
        model = EITurnkeyBatch
        fields = '__all__'



class EITurnkeyBatchEInvoiceSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:eiturnkeybatcheinvoice-detail")
    ei_turnkey_batch_dict = EITurnkeyBatchSerializer(read_only=True, source="ei_turnkey_batch")
    


    class Meta:
        model = EITurnkeyBatchEInvoice
        fields = '__all__'