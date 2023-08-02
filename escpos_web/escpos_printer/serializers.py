import datetime
import logging
import pytz

from django.conf import settings
from django.contrib.auth.models import User, Group, Permission, AnonymousUser 
from django.contrib.contenttypes.models import ContentType
from django.utils.timezone import utc, now
from django.utils.translation import gettext_lazy as _
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
from escpos_printer.models import (
    Printer,
    TEAWeb,
)


class PrinterSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="escposwebapi:printer-detail", lookup_field='pk')
    get_type_display = CharField(read_only=True)
    get_profile_display = CharField(read_only=True)
    get_receipt_type_display = CharField(read_only=True)
    get_default_encoding_display = CharField(read_only=True)



    class Meta:
        model = Printer
        fields = '__all__'



class TEAWebSerializer(ModelSerializer):
    resource_uri = HyperlinkedIdentityField(
        view_name="escposwebapi:teaweb-detail", lookup_field='pk')
    mask_hash_key = CharField(read_only=True)



    class Meta:
        model = TEAWeb
        fields = [
            'id', 'resource_uri',
            'name', 'url', 'slug', 'mask_hash_key', 'now_use',
        ]
        extra_kwargs = {
            'hash_key': {'write_only': True},
        }