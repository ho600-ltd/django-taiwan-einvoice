from django.apps import AppConfig


class TaiwanEinvoiceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'taiwan_einvoice'


    def ready(self):
        import taiwan_einvoice.signals