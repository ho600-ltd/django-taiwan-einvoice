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
)


class FROM_CONFIGSerializer(ModelSerializer):
    class Meta:
        model = FROM_CONFIG
        fields = '__all__'


