import logging
logger = logging.getLogger(__name__)

from django.contrib import admin

from .models import EInvoiceSellerAPI


class EInvoiceSellerAPIAdmin(admin.ModelAdmin):
    pass



admin.site.register(EInvoiceSellerAPI, EInvoiceSellerAPIAdmin)