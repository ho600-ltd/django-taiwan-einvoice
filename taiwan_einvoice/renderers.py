import re
import string

from io import BytesIO

from django.utils.translation import pgettext_lazy

from rest_framework.renderers import BrowsableAPIRenderer


class TEBrowsableAPIRenderer(BrowsableAPIRenderer):
    template = "taiwan_einvoice/api.html"