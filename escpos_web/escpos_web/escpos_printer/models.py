import usb.core, usb.util
from escpos.printer import Usb
from django.db import models
from jsonfield import JSONField



class UsbZhHant(Usb):
    def __init__(self, *args, **kwargs):
        super(UsbZhHant, self).__init__(*args, **kwargs)
        self.charcode(code='CP1252')
        

    def text(self, text, *args, **kwargs):
        return super(UsbZhHant, self).text(text.encode('cp950').decode('latin1'), *args, **kwargs)



class Printer(models.Model):
    PRINTER_TYPES = (
        ("n", "Network"),
        ("p", "Parallel"),
        ("s", "Serial"),
        ("u", "USB"),
    )
    SUPPORT_PRINTERS = (
        ("00", "TM-T88IV"),
        ("01", "TM-T88V"),
    )
    PRINTERS_DICT = {
        value:key for key, value in dict(SUPPORT_PRINTERS).iteritems()
    }
    RECEIPT_TYPES = (
        ('5', '58mm Receipt'),
        ('6', '58mm E-Invoice'),
        ('8', '80mm Receipt'),
    )
    serial_number = models.CharField(max_length=128, unique=True)
    nickname = models.CharField(max_length=64, unique=True)
    type = models.CharField(max_length=1, choices=PRINTER_TYPES)
    vendor_number = models.SmallInteger()
    product_number = models.SmallInteger()
    profile = models.CharField(max_length=2, choices=SUPPORT_PRINTERS)
    receipt_type = models.CharField(max_length=1, choices=RECEIPT_TYPES)
    


    @classmethod
    def load_printers(cls, idVendor=0x04b8, idProduct=0x0202):
        printers = {}
        for dev in usb.core.find(find_all=True, idVendor=idVendor, idProduct=idProduct):
            serial_number = usb.util.get_string(dev, dev.iSerialNumber)
            product = usb.util.get_string(dev, dev.iProduct)
            try:
                printer = cls.objects.get(serial_number=serial_number)
            except cls.DoesNotExist:
                max_length = cls._meta.get_field('nickname').max_length
                printer = cls(serial_number=serial_number, nickname=serial_number[-1*max_length:])
            printer.type = "s"
            printer.vendor_number = dev.idVendor
            printer.product_number = dev.idProduct
            printer.profile = PRINTERS_DICT['product']
            printer.save()
            printers[serial_number] = UsbZhHant(printer.vendor_number, printer.product_number, usb_args={
                "address": dev.address, "bus": dev.bus
            })
        return printers


    def get_escpos_printer(self):
        if 'u' == self.type:
            for dev in usb.core.find(find_all=True, idVendor=self.vendor_number, idProduct=self.product_number):
                if self.serial_number == usb.util.get_string(dev, dev.iSerialNumber):
                    return UsbZhHant(self.vendor_number, self.product_number, usb_args={
                        "address": dev.address, "bus": dev.bus
                    })


    @property
    def meet_to_tw_einvoice_standard(self):
        if '6' == self.receipt_type:
            return True
        else:
            return False


    @property
    def is_connected(self):
        if 'u' == self.type:
            for dev in usb.core.find(find_all=True, idVendor=self.vendor_number, idProduct=self.product_number):
                if self.serial_number == usb.util.get_string(dev, dev.iSerialNumber):
                    return True
        return False



class TEWeb(models.Model):
    url = models.CharField(max_length=755)
    api_key = models.CharField(max_length=64)



class ReceiptLog(models.Model):
    receipt_json_format = """{
        "meet_to_tw_einvoice_standard": [False/True],
        "track_no": "String",
        "generate_time": "UTC datetime",
        "width": [58mm/80mm],
        "content": [
            {"type": "text", "size": "", "align": "", "text": ""},
            {"type": "barcode", "size": "", "align": "", "code": ""},
            {"type": "qrcode_pair", "size": "", "align": "", "qr_text1": "", "qr_text2": ""},
            ...
        ]
}
"""
    te_web = models.ForeignKey(TEWeb, on_delete=models.DO_NOTHING)
    printer = models.ForeignKey(Printer, on_delete=models.DO_NOTHING)
    meet_to_tw_einvoice_standard = models.BooleanField(default=False)
    track_no = models.CharField(max_length=32)
    copy_order = models.SmallInteger(default=0)
    generate_time = models.DateTimeField()
    print_time = models.DateTimeField(auto_now_add=True)
    content = JSONField()


    
    class Meta:
        unique_together = (('meet_to_tw_einvoice_standard', 'track_no', 'copy_order', ), )