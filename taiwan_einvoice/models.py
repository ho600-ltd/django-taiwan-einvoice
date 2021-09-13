from hashlib import sha1
from random import random, randint
from django.db import models
from django.utils.translation import ugettext_lazy as _


KEY_CODE_SET = [
    'C', 'W', 'B', 'E', 'R', 'T', 'Y','6', '7', '8',
    'U', 'P', 'K', 'X', 'A', 'S', 'D', 'V', 'F', 'H',
    '3', '5',
]
def get_codes(verify_id, seed=0):
    if seed <= 0:
        seed = randint(234256, 702768)
    seed = seed % 234256
    code1_n = (seed // 10648)
    code1 = KEY_CODE_SET[code1_n]
    code2_n = (seed % 10648) // 484
    code2 = KEY_CODE_SET[code2_n]
    code3_n = (seed % 10648) % 484 // 22
    code3 = KEY_CODE_SET[code3_n]
    code4_n = (seed % 10648) % 484 % 22
    code4 = KEY_CODE_SET[code4_n]
    code5 = KEY_CODE_SET[((code1_n + code2_n + code3_n + code4_n) ** 3 + verify_id) % 22]
    return ''.join((code1, code2, code3, code4, code5))



class ESCPOSWeb(models.Model):
    name = models.CharField(max_length=32)
    slug = models.CharField(max_length=4, default='')
    hash_key = models.CharField(max_length=40, default='')



    def verify_token_auth(self, seed, verify_value):
        if self.escposwebconnectionlog_set.filter(seed=seed).exists():
            return False
        elif verify_value == sha1("{}-{}".format(self.slug, seed).encode('utf-8')).hexdigest():
            escpos_web_cl = ESCPOSWebConnectionLog(escpos_web=self, seed=seed)
            escpos_web_cl.save()
            return True
        return False


    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
        need_save = False
        if not self.slug:
            while True:
                slug = get_codes(self.pk)
                if not ESCPOSWeb.objects.filter(slug=slug).exists():
                    self.slug = slug
                    break
            need_save = True
        if not self.hash_key:
            self.hash_key = sha1(str(random()).encode('utf-8')).hexdigest()
            need_save = True
        if need_save:
            super().save(*args, **kwargs)



class ESCPOSWebConnectionLog(models.Model):
    create_time = models.DateTimeField(auto_now_add=True)
    escpos_web = models.ForeignKey(ESCPOSWeb, on_delete=models.DO_NOTHING)
    seed = models.CharField(max_length=15)


    class Meta:
        unique_together = (('escpos_web', 'seed', ), )


class Printer(models.Model):
    RECEIPT_TYPES = (
        ('5', _('58mm Receipt')),
        ('6', _('58mm E-Invoice')),
        ('8', _('80mm Receipt')),
    )
    escpos_web = models.ForeignKey(ESCPOSWeb, on_delete=models.DO_NOTHING)
    serial_number = models.CharField(max_length=128, unique=True)
    nickname = models.CharField(max_length=64, unique=True)
    receipt_type = models.CharField(max_length=1, choices=RECEIPT_TYPES)
    


class TurnkeyWeb(models.Model):
    name = models.CharField(max_length=32)
    hash_key = models.CharField(max_length=40)
    transport_id = models.CharField(max_length=10)
    party_id = models.CharField(max_length=10)
    routing_id = models.CharField(max_length=39)
    


class IdentifierRule(object):
    def verify_identifier(self):
        identifier = self.identifier
        return False



class LegalEntity(models.Model, IdentifierRule):
    identifier = models.CharField(max_length=8, null=False, blank=False, db_index=True)
    name = models.CharField(max_length=60, default='', db_index=True)
    address = models.CharField(max_length=100, default='', db_index=True)
    person_in_charge = models.CharField(max_length=30, default='', db_index=True)
    telephone_number = models.CharField(max_length=26, default='', db_index=True)
    facsimile_number = models.CharField(max_length=26, default='', db_index=True)
    email_address = models.CharField(max_length=80, default='', db_index=True)
    customer_number_char = models.CharField(max_length=20, default='', db_index=True)
    @property
    def customer_number(self):
        if not self.customer_number_char:
            return str(self.pk)
        else:
            return self.currency_type_char
    @customer_number.setter
    def customer_number(self, char):
        self.currency_type_char = char
        self.save()
    role_remark = models.CharField(max_length=40, default='', db_index=True)


    class Meta:
        unique_together = (('identifier', 'customer_number_char'), )



class Seller(models.Model):
    legal_entity = models.ForeignKey(LegalEntity, on_delete=models.DO_NOTHING)
    print_with_seller_optional_fields = models.BooleanField(default=False)
    print_with_buyer_optional_fields = models.BooleanField(default=False)
    


class SellerInvoiceTrackNo(models.Model):
    turnkey_web = models.ForeignKey(TurnkeyWeb, on_delete=models.DO_NOTHING)
    seller = models.ForeignKey(Seller, on_delete=models.DO_NOTHING)
    type_choices = (
        ('07', _('General')),
        ('08', _('Special')),
    )
    type = models.CharField(max_length=2, default='07', choices=type_choices)
    begin_time = models.DateTimeField()
    end_time = models.DateTimeField()
    track = models.CharField(max_length=2)
    begin_no = models.SmallIntegerField()
    end_no = models.SmallIntegerField()



class EInvoice(models.Model):
    only_fields_can_update = ['print_mark']
    seller_invoice_track_no = models.ForeignKey(SellerInvoiceTrackNo, on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=2, default='07', choices=SellerInvoiceTrackNo.type_choices)
    track = models.CharField(max_length=2, db_index=True)
    no = models.SmallIntegerField(db_index=True)
    npoban = models.CharField(max_length=7, default='', db_index=True)
    @property
    def donate_mark(self):
        if self.npoban:
            return '1'
        else:
            return '0'
    print_mark = models.BooleanField(default=False)
    random_number = models.CharField(max_length=4, null=False, blank=False, db_index=True)
    generate_time = models.DateTimeField(auto_now_add=True, db_index=True)

    seller = models.ForeignKey(LegalEntity, related_name="as_seller_own_einvoice_set", on_delete=models.DO_NOTHING)
    seller_identifier = models.CharField(max_length=8, null=False, blank=False, db_index=True)
    seller_name = models.CharField(max_length=60, default='', db_index=True)
    seller_address = models.CharField(max_length=100, default='', db_index=True)
    seller_person_in_charge = models.CharField(max_length=30, default='', db_index=True)
    seller_telephone_number = models.CharField(max_length=26, default='', db_index=True)
    seller_facsimile_number = models.CharField(max_length=26, default='', db_index=True)
    seller_email_address = models.CharField(max_length=80, default='', db_index=True)
    seller_customer_number = models.CharField(max_length=20, default='', db_index=True)
    seller_role_remark = models.CharField(max_length=40, default='', db_index=True)
    buyer = models.ForeignKey(LegalEntity, related_name="as_buyer_own_einvoice_set", on_delete=models.DO_NOTHING)
    buyer_identifier = models.CharField(max_length=8, null=False, blank=False, db_index=True)
    buyer_name = models.CharField(max_length=60, default='', db_index=True)
    buyer_address = models.CharField(max_length=100, default='', db_index=True)
    buyer_person_in_charge = models.CharField(max_length=30, default='', db_index=True)
    buyer_telephone_number = models.CharField(max_length=26, default='', db_index=True)
    buyer_facsimile_number = models.CharField(max_length=26, default='', db_index=True)
    buyer_email_address = models.CharField(max_length=80, default='', db_index=True)
    buyer_customer_number = models.CharField(max_length=20, default='', db_index=True)
    buyer_role_remark = models.CharField(max_length=40, default='', db_index=True)

    #TODO
    #details
    #amounts


    class Meta:
        unique_together = (('seller_invoice_track_no', 'track', 'no'), )
    

    def set_print_mark_true(self):
        if False == self.print_mark:
            self.print_mark = True
            self.update(update_fields=self.only_fields_can_update)
    

    def update(self, *args, **kwargs):
        if self.only_fields_can_update == kwargs.get('update_fields', []):
            super().update(update_fields=self.only_fields_can_update)


    def delete(self, *args, **kwargs):
        raise Exception('Can not delete')


    def save(self, *args, **kwargs):
        if not self.pk:
            seller = self.seller_invoice_track_no.seller
            while True:
                random_number = '{04d}'.format(randint(0, 10000))
                objs = self._meta.model.objects.filter(seller_invoice_track_no__seller=seller).order_by('-id')[:1000]
                if not objs.exists():
                    break
                else:
                    obj = objs[len(objs)-1]
                    if not self._meta.model.objects.filter(id__gte=obj.id,
                                                           seller_invoice_track_no__seller=seller,
                                                           random_number=random_number).exists():
                        break
            self.random_number = random_number
            super().save(*args, **kwargs)