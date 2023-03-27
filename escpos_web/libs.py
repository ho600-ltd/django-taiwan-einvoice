#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import time, netifaces, urllib.request, datetime
from escpos.printer import Usb



class UsbZhHant(Usb):
    def __init__(self, *args, **kwargs):
        super(UsbZhHant, self).__init__(*args, **kwargs)
        self.default_encoding = kwargs.get('default_encoding', 'CP950').upper()
        if 'CP950' == self.default_encoding:
            charcode = 'CP1252'
        elif 'GB18030' == self.default_encoding:
            charcode = 'ISO_8859-2'
        else:
            self.default_encoding = 'CP950'
            charcode = 'CP1252'
        try: self.charcode(code=charcode)
        except KeyError: pass


    def text(self, text, *args, **kwargs):
        if 'CP950' == self.default_encoding:
            return super(UsbZhHant, self).text(text.encode(self.default_encoding.lower()).decode('latin1'), *args, **kwargs)
        elif 'GB18030' == self.default_encoding:
            return super(UsbZhHant, self).text(text.encode(self.default_encoding.lower()).decode('latin2'), *args, **kwargs)

    
    def barcode(self, code, bc, height=64, width=3, pos="BELOW", font="A",
                align_ct=True, function_type=None, check=True):
        from escpos.escpos import (six, BARCODE_TYPES, NUL,
                                   BarcodeTypeError, BarcodeCodeError, BarcodeSizeError,
                                   BARCODE_WIDTH, BARCODE_HEIGHT,
                                   BARCODE_FONT_A, BARCODE_FONT_B,
                                   TXT_STYLE,
                                   BARCODE_TXT_OFF, BARCODE_TXT_BTH, BARCODE_TXT_ABV, BARCODE_TXT_BLW,)

        if function_type is None:
            # Choose the function type automatically.
            if bc in BARCODE_TYPES['A']:
                function_type = 'A'
            else:
                if bc in BARCODE_TYPES['B']:
                    if not self.profile.supports(bc):
                        raise BarcodeTypeError((
                            "Barcode type '{bc} not supported for "
                            "the current printer profile").format(bc=bc))
                    function_type = 'B'
                else:
                    raise BarcodeTypeError((
                        "Barcode type '{bc} is not valid").format(bc=bc))

        bc_types = BARCODE_TYPES[function_type.upper()]
        if bc.upper() not in bc_types.keys():
            raise BarcodeTypeError((
                "Barcode '{bc}' not valid for barcode function type "
                "{function_type}").format(
                    bc=bc,
                    function_type=function_type,
                ))

        if check and not self.check_barcode(bc, code):
            raise BarcodeCodeError((
                "Barcode '{code}' not in a valid format for type '{bc}'").format(
                code=code,
                bc=bc,
            ))

        # Align Bar Code()
        if align_ct:
            self._raw(TXT_STYLE['align']['center'])
        # Height
        if 1 <= height <= 255:
            self._raw(BARCODE_HEIGHT + six.int2byte(height))
        else:
            raise BarcodeSizeError("height = {height}".format(height=height))
        # Width
        if 1 <= width <= 6:
            self._raw(BARCODE_WIDTH + six.int2byte(width))
        else:
            raise BarcodeSizeError("width = {width}".format(width=width))
        # Font
        if font.upper() == "B":
            self._raw(BARCODE_FONT_B)
        else:  # DEFAULT FONT: A
            self._raw(BARCODE_FONT_A)
        # Position
        if pos.upper() == "OFF":
            self._raw(BARCODE_TXT_OFF)
        elif pos.upper() == "BOTH":
            self._raw(BARCODE_TXT_BTH)
        elif pos.upper() == "ABOVE":
            self._raw(BARCODE_TXT_ABV)
        else:  # DEFAULT POSITION: BELOW
            self._raw(BARCODE_TXT_BLW)

        self._raw(bc_types[bc.upper()])

        if function_type.upper() == "B":
            self._raw(six.int2byte(len(code)))

        # Print Code
        if code:
            self._raw(code.encode())
        else:
            raise BarcodeCodeError()

        if function_type.upper() == "A":
            self._raw(NUL)



def get_tea_web_name():
    from escpos_printer.models import TEAWeb
    tea_webs = TEAWeb.objects.filter(now_use=True).order_by('id')
    if tea_webs:
        return tea_webs[0].name
    else:
        return '無可使用的伺服器'


def get_public_ip():
    no_ip = '?.?.?.?'
    i = 0
    while i < 10:
        try:
            external_ip = urllib.request.urlopen('https://ipv4.icanhazip.com').read().strip().decode('utf-8')
        except:
            external_ip = no_ip
        if no_ip == external_ip:
            i += 1
            time.sleep(3)
        else:
            break
    return external_ip


def get_eths():
    eths = []
    for eth in netifaces.interfaces():
        if 'lo' == eth: continue
        i = netifaces.ifaddresses(eth)
        try: ip = netifaces.ifaddresses(eth)[netifaces.AF_INET][0]['addr']
        except: pass
        else: eths.append((eth, ip))
    return eths


def get_boot_seed():
    try:
        seed = open('/var/run/boot_random_seed', 'r').read()[:3].upper()
    except:
        seed = '???'
    return seed


def get_hour_minute():
    return datetime.datetime.now().strftime('%H:%M')
