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



class TASK_CONFIGSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(view_name="turnkeywrapperapi:taskconfig-detail")
    


    class Meta:
        model = TASK_CONFIG
        fields = '__all__'


