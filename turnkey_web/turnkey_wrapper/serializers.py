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
    TASK_CONFIG,
)


class FROM_CONFIGSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:fromconfig-detail")

    class Meta:
        model = FROM_CONFIG
        fields = '__all__'



class SCHEDULE_CONFIGSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:taskconfig-detail")
    


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


