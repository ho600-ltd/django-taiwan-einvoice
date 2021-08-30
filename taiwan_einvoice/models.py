from django.db import models
from django.utils.translation import ugettext_lazy as _


class ESCPOSWeb(models.Model):
    name = models.CharField(max_length=32)
    hash_key = models.CharField(max_length=40)



class TurnkeySWeb(models.Model):
    name = models.CharField(max_length=32)
    hash_key = models.CharField(max_length=40)



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
        unique_together = (('identifier', 'customer_number'), )



class Seller(models.Model):
    legal_entity = models.ForeignKey(LegalEntity)
    print_with_seller_optional_fields = models.BooleanField(default=False)
    print_with_buyer_optional_fields = models.BooleanField(default=False)
    


class SellerInvoiceTrackNo(models.Model):
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