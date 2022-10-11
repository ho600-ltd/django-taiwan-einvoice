import usb.core, usb.util, re, json, qrcode, os, subprocess
from random import random
from hashlib import sha1
from PIL import Image
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _



class Printer(models.Model):
    PRINTER_TYPES = (
        ("n", "Network"),
        ("p", "Parallel"),
        ("s", "Serial"),
        ("u", "USB"),
    )
    SUPPORT_PRINTERS = (
        ("-1", "default"),
        ("00", "TM-T88IV"),
        ("01", "TM-T88V"),
    )
    PRINTERS_DICT = {
        value:key for key, value in dict(SUPPORT_PRINTERS).items()
    }
    RECEIPT_TYPES = (
        ('0', _("DOES NOT WORK")),
        ('5', _('58mm Receipt')),
        ('6', _('58mm E-Invoice')),
        ('8', _('80mm Receipt')),
    )
    ENCODINGS = (
        ('B', 'CP950'),
        ('G', "GB18030"),
    )
    PRINTERS = {}
    serial_number = models.CharField(max_length=128, unique=True)
    nickname = models.CharField(max_length=64, unique=True)
    type = models.CharField(max_length=1, choices=PRINTER_TYPES)
    vendor_number = models.SmallIntegerField()
    product_number = models.SmallIntegerField()
    profile = models.CharField(max_length=2, choices=SUPPORT_PRINTERS)
    receipt_type = models.CharField(max_length=1, choices=RECEIPT_TYPES, default='0')
    default_encoding = models.CharField(max_length=1, choices=ENCODINGS, default='B')


    def __str__(self):
        return "{}({}-{})".format(self.nickname, self.get_type_display(), self.get_receipt_type_display())
    


    @classmethod
    def load_printers(cls, idVendor_idProduct_set=((0x04b8, 0x0202),), setup=True):
        from libs import UsbZhHant
        for k, v in cls.PRINTERS.items():
            if isinstance(v.get('printer_device', None), UsbZhHant):
                v['printer_device'].close()
        cls.PRINTERS = {}

        for (idVendor, idProduct) in idVendor_idProduct_set:
            for dev in usb.core.find(find_all=True, idVendor=idVendor, idProduct=idProduct):
                serial_number = usb.util.get_string(dev, dev.iSerialNumber)
                product = usb.util.get_string(dev, dev.iProduct)
                try:
                    printer = cls.objects.get(serial_number=serial_number)
                except cls.DoesNotExist:
                    max_length = cls._meta.get_field('nickname').max_length
                    printer = cls(serial_number=serial_number, nickname=serial_number[-1*max_length:])
                printer.type = "u"
                printer.vendor_number = dev.idVendor
                printer.product_number = dev.idProduct
                printer.profile = cls.PRINTERS_DICT.get(product, '-1')
                printer.save()
                if setup:
                    printer_device = UsbZhHant(printer.vendor_number,
                                               printer.product_number,
                                               usb_args={"address": dev.address, "bus": dev.bus},
                                               profile=printer.get_profile_display(),
                                               default_encoding=self.get_default_encoding_display(),
                                              )
                    cls.PRINTERS[serial_number] = {
                        'nickname': printer.nickname,
                        'receipt_type': printer.receipt_type,
                        'printer_device': printer_device,
                    }
                else:
                    cls.PRINTERS[serial_number] = {
                        'nickname': printer.nickname,
                        'receipt_type': printer.receipt_type,
                    }
        return cls.PRINTERS


    def get_escpos_printer(self, setup=True):
        if 'u' == self.type:
            from libs import UsbZhHant
            usb_zhhant = Printer.PRINTERS.get(self.serial_number, {}).get('printer_device', None)
            if usb_zhhant:
                usb_zhhant.close()
                del Printer.PRINTERS[self.serial_number]
            for dev in usb.core.find(find_all=True, idVendor=self.vendor_number, idProduct=self.product_number):
                if self.serial_number == usb.util.get_string(dev, dev.iSerialNumber):
                    if setup:
                        usb_zhhant = UsbZhHant(self.vendor_number, self.product_number,
                                               usb_args={"address": dev.address, "bus": dev.bus},
                                               profile=self.get_profile_display(),
                                               default_encoding=self.get_default_encoding_display(),
                                              )
                        Printer.PRINTERS[self.serial_number] = {
                            'nickname': self.nickname,
                            'receipt_type': self.receipt_type,
                            'printer_device': usb_zhhant,
                        }
                    else:
                        Printer.PRINTERS[self.serial_number] = {
                            'nickname': self.nickname,
                            'receipt_type': self.receipt_type,
                        }
                    return Printer.PRINTERS[self.serial_number]


    @property
    def meet_to_tw_einvoice_standard(self):
        if '6' == self.receipt_type:
            return True
        else:
            return False


    @property
    def is_connected(self, setup=True):
        if 'u' == self.type:
            from libs import UsbZhHant
            for dev in usb.core.find(find_all=True, idVendor=self.vendor_number, idProduct=self.product_number):
                if self.serial_number == usb.util.get_string(dev, dev.iSerialNumber):
                    if self.serial_number not in Printer.PRINTERS:
                        if setup:
                            usb_zhhant = UsbZhHant(self.vendor_number, self.product_number,
                                                   usb_args={"address": dev.address, "bus": dev.bus },
                                                   profile=self.get_profile_display(),
                                                   default_encoding=self.get_default_encoding_display(),
                                                  )
                            Printer.PRINTERS[self.serial_number] = {
                                'nickname': self.nickname,
                                'receipt_type': self.receipt_type,
                                'printer_device': usb_zhhant,
                            }
                        else:
                            Printer.PRINTERS[self.serial_number] = {
                                'nickname': self.nickname,
                                'receipt_type': self.receipt_type,
                            }
                    return True
            if self.serial_number in Printer.PRINTERS:
                try:
                    Printer.PRINTERS[self.serial_number]['printer_device'].close()
                except:
                    pass
                del Printer.PRINTERS[self.serial_number]
        return False



class TEAWeb(models.Model):
    name = models.CharField(max_length=8)
    url = models.CharField(max_length=755)
    slug = models.CharField(max_length=5, unique=True)
    hash_key = models.CharField(max_length=40)
    @property
    def mask_hash_key(self):
        return self.hash_key[:4] + '********************************' + self.hash_key[-4:]
    now_use = models.BooleanField(default=True)


    def generate_token_auth(self):
        seed = sha1(str(random()).encode('utf-8')).hexdigest()[:15]
        verify_value = sha1("{}-{}".format(self.slug, seed).encode('utf-8')).hexdigest()
        return "{}-{}-{}".format(self.slug, seed, verify_value)
    

    def save(self, *args, **kwargs):
        if True == self.now_use:
            if self.id:
                TEAWeb.objects.exclude(id=self.id).update(now_use=False)
            else:
                TEAWeb.objects.all().update(now_use=False)
            RESTART_PROCESSES_AFTER_SET_NOW_USE = os.getenv("RESTART_PROCESSES_AFTER_SET_NOW_USE", "")
            print(RESTART_PROCESSES_AFTER_SET_NOW_USE)
            if RESTART_PROCESSES_AFTER_SET_NOW_USE and "asgi0" in RESTART_PROCESSES_AFTER_SET_NOW_USE:
                subprocess.run(['sudo', 'supervisorctl', 'restart', RESTART_PROCESSES_AFTER_SET_NOW_USE])
        return super().save(*args, **kwargs)




class Receipt(models.Model):
    receipt_json_format = """{
        "meet_to_tw_einvoice_standard": [False/True],
        "track_no": "String",
        "generate_time": "datetime_str",
        "width": [58mm/80mm],
        "content": [
            {"type": "text", "size": "", "align": "", "text": ""},
            {"type": "barcode", "size": "", "align": "", "code": ""},
            {"type": "qrcode_pair", "size": "", "align": "", "qr_text1": "", "qr_text2": ""},
            ...
        ]
}
"""
    tw_einvoice_demo_json = """{
    "meet_to_tw_einvoice_standard": true,
    "track_no": "HO24634102",
    "generate_time": "2021-09-10 11:33:00+0800",
    "width": "58mm",
    "content": [
        {"type": "text", "custom_size": true, "width": 1, "height": 2, "align": "center", "text": "電 子 發 票 證 明 聯"},
        {"type": "text", "custom_size": true, "width": 1, "height": 1, "align": "left", "text": ""},
        {"type": "text", "custom_size": true, "width": 2, "height": 2, "align": "center", "text": "110年07-08月"},
        {"type": "text", "custom_size": true, "width": 2, "height": 2, "align": "center", "text": "HO-24634102"},
        {"type": "text", "custom_size": true, "width": 1, "height": 1, "align": "left", "text": ""},
        {"type": "text", "custom_size": true, "width": 1, "height": 1, "align": "left", "text": " 2021-09-08 09:06:04"},
        {"type": "text", "custom_size": true, "width": 1, "height": 1, "align": "left", "text": " 隨機碼 3760 總計 99999999"},
        {"type": "text", "custom_size": true, "width": 1, "height": 1, "align": "left", "text": " 賣方 24634102 買方 24634102"},
        {"type": "text", "custom_size": true, "width": 1, "height": 1, "align": "left", "text": ""},
        {"type": "barcode", "align_ct": true, "width": 1, "height": 64, "pos": "OFF", "code": "CODE39", "barcode": "11008HO246341023760"},
        {"type": "qrcode_pair", "center": false,
         "qr1_str": "HO246341021100908888899999999999999992463410224634102ydXZt4LAN1UHN/j1juVcRA==:**********:1:1:1:",
         "qr2_str": "**何六百專業諮詢服務:1:99999999"},
        {"type": "text", "custom_size": true, "width": 1, "height": 1, "align": "left", "text": " 退貨須憑證明聯正本辦理"}
    ]
}
"""
    tea_web = models.ForeignKey(TEAWeb, on_delete=models.DO_NOTHING)
    meet_to_tw_einvoice_standard = models.BooleanField(default=False)
    track_no = models.CharField(max_length=32)
    random_number = models.CharField(max_length=4, default='')
    generate_time = models.DateTimeField()
    WIDTHS = (
        ('5', '58mm'),
        ('8', '80mm'),
    )
    WIDTHS_DICT = {
        value:key for key, value in dict(WIDTHS).items()
    }
    original_width = models.CharField(max_length=1, choices=WIDTHS, default='5')
    content = models.JSONField()


    
    class Meta:
        unique_together = (('meet_to_tw_einvoice_standard', 'track_no', 'random_number', ), )


    @classmethod
    def create_receipt(cls, tea_web, message, re_print_original_copy=False):
        J = json.loads(message)
        random_number = J.get('random_number', '')
        try:
            obj = cls.objects.get(meet_to_tw_einvoice_standard=J['meet_to_tw_einvoice_standard'],
                                  track_no=J['track_no'], random_number=random_number)
        except cls.DoesNotExist:
            obj = cls(tea_web=tea_web,
                      meet_to_tw_einvoice_standard=J['meet_to_tw_einvoice_standard'],
                      track_no=J['track_no'],
                      random_number=random_number,
                      generate_time=J['generate_time'],
                      original_width=cls.WIDTHS_DICT[J['width']],
                      content=J["content"])
            obj.save()
        else:
            if re_print_original_copy or False == J['meet_to_tw_einvoice_standard']:
                obj.content = J["content"]
                obj.save()
        return obj


    def print(self, printer, print_mark=False, re_print_original_copy=False, extra_content=[]):
        copy_order = ReceiptLog.objects.filter(printer=printer, receipt=self).count() + 1
        rl = ReceiptLog(printer=printer,
                        receipt=self,
                        print_mark=print_mark,
                        re_print_original_copy=re_print_original_copy,
                        copy_order=copy_order,
                        )
        rl.save()
        try:
            rl.print(extra_content=extra_content)
        except Exception as e:
            rl.delete()
            return (False, "Exception in Receipt: {}".format(e))
        else:
            return True
        


TW_EINVOICE_TITLE_RE = re.compile('電[ 　]*子[ 　]*發[ 　]*票[ 　]*證[ 　]*明[ 　]*聯[ 　]*$')
TW_EINVOICE_2_COPY_TITLE_RE = re.compile('補[ 　]*印[ 　]*$')
class ReceiptLog(models.Model):
    printer = models.ForeignKey(Printer, on_delete=models.DO_NOTHING)
    receipt = models.ForeignKey(Receipt, on_delete=models.DO_NOTHING)
    print_mark = models.BooleanField(default=False)
    re_print_original_copy = models.BooleanField(default=False)
    copy_order = models.SmallIntegerField(default=0)
    print_time = models.DateTimeField(null=True)


    
    class Meta:
        unique_together = (('printer', 'receipt', 'copy_order', ), )



    def print(self, extra_content=[]):
        if self.print_time:
            return False
        if self.printer.is_connected:
            pd = Printer.PRINTERS.get(self.printer.serial_number, {}).get('printer_device', None)
            if not pd:
                pd = self.printer.get_escpos_printer().get('printer_device', None)
        else:
            pd = self.printer.get_escpos_printer().get('printer_device', None)

        if not pd:
            return False

        type_method = {
            "ln": self.print_ln,
            "text": self.print_text,
            "barcode": self.print_barcode,
            "qrcode_pair": self.print_qrcode_pair,
        }
        for line in self.receipt.content + extra_content:
            type_method[line['type']](pd, line)
        pd.cut(feed=False)
        self.print_time = now()
        self.save()
    

    def print_ln(self, printer_device, line):
        printer_device.ln(line['count'])


    def print_text(self, printer_device, line):
        """ Escpos.set's kwargs:
            {align='left', font='a', bold=False, underline=0, width=1,
             height=1, density=9, invert=False, smooth=False, flip=False,
             double_width=False, double_height=False, custom_size=False}
        """
        default_args = ['align', 'font', 'bold', 'underline', 'width',
                        'height', 'density', 'invert', 'smooth', 'flip',
                        'double_width', 'double_height', 'custom_size']
        d = {}
        for k in default_args:
            if k in line:
                d[k] = line[k]
        if '8' == self.printer.receipt_type and '5' == self.receipt.original_width:
            d['align'] = 'left'
        text = line['text']
        if ((self.receipt.meet_to_tw_einvoice_standard
                and self.re_print_original_copy == False
                and self.copy_order > 1
                and TW_EINVOICE_TITLE_RE.search(text)
                and not TW_EINVOICE_2_COPY_TITLE_RE.search(text)
            ) or (self.receipt.meet_to_tw_einvoice_standard
                and self.re_print_original_copy == False
                and self.print_mark
                and TW_EINVOICE_TITLE_RE.search(text)
                and not TW_EINVOICE_2_COPY_TITLE_RE.search(text)
            )):
            text += '補印'
        printer_device.set(**d)

        default_encoding = self.printer.get_default_encoding_display().upper()
        if 'CP950' == default_encoding:
            map_encoding = 'cp950'
        elif 'GB18030' == default_encoding:
            map_encoding = 'gbk'
        else:
            map_encoding = 'utf-8'
        valid_texts = []
        for _t in text:
            try:
                _o = _t.encode(map_encoding)
            except UnicodeEncodeError:
                _o = '○'.encode(map_encoding)
            valid_texts.append(_o.decode(map_encoding))
        printer_device.textln(''.join(valid_texts))
        printer_device.set()


    def print_barcode(self, printer_device, line):
        """ Escpos.barcode's kwargs:
            {height=64, width=3, pos="BELOW", font="A",
             align_ct=True, function_type=None, check=True}
        """
        if not line.get('barcode', ''):
            printer_device.ln(1)
            return

        default_args = ['height', 'width', 'pos', 'font',
                        'align_ct', 'function_type', 'check']
        d = {}
        for k in default_args:
            if k in line:
                d[k] = line[k]
        if '8' == self.printer.receipt_type and '5' == self.receipt.original_width:
            d['align_ct'] = False
        printer_device.barcode(line['barcode'], line['code'], **d)

    
    def print_qrcode_pair(self, printer_device, line):
        """ Escpos.image's kwargs:
            {high_density_vertical=True, high_density_horizontal=True, impl="bitImageRaster",
             fragment_height=960, center=False}
        """
        default_args = ['high_density_vertical', 'high_density_horizontal', 'impl',
                        'fragment_height', 'center']
        d = {}
        for k in default_args:
            if k in line:
                d[k] = line[k]
        if '8' == self.printer.receipt_type and '5' == self.receipt.original_width:
            d['center'] = False
        images = []
        for s in [line['qr1_str'], line['qr2_str']]:
            qr = qrcode.QRCode(version=1,
                               error_correction=qrcode.constants.ERROR_CORRECT_L,
                               box_size=5,
                               border=0)
            qr.add_data(s)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((154, 154))
            images.append(img)
        qr_image = Image.new("RGB", (347, 180), color='white')
        qr_image.paste(images[0], (13, 13))
        qr_image.paste(images[1], (193, 13))
        printer_device.image(qr_image, **d)
