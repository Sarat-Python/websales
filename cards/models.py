'''
PIT_STOP_RECHARGE_BEGIN_TAG
*
* Pit Stop Recharge CONFIDENTIAL
*
* COPYRIGHT Pit Stop Recharge P/L 2011, 2014
* All Rights Reserved
*
* The source code for this program is not published or otherwise 
* divested of its trade secrets, irrespective of what has been 
* deposited with the Australian Copyright Office. 
*
PIT_STOP_RECHARGE_END_TAG
'''
'''
Begin Change Log **************************************************************
                                                                      
  Itr       Def/Req     Userid      Date          Description
  -----     --------    --------    --------    --------------------------------------
  Story #31  Tasks #36   NaveeN      26/04/2014  Added model GiftCards
 End Change Log ***************************************************************
'''

from django.db import models
from django.utils import timezone
from users.models import WebUser
from cards.card_utils import verify_card_length
from cards.card_info import CARD_TYPES
# Create your models here.


class shopcart(models.Model):
    shopcart_id = models.CharField( max_length=100)
    activate_card_batch_id = models.CharField( max_length=100)    
    gift_card_id = models.CharField(max_length=50)
    card_type = models.CharField(max_length=100)
    card_flavour = models.CharField(max_length=255)
    upc_code = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)
    total_amount = models.CharField(max_length=50) 
    card_flavour_image_file = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    createdby = models.ForeignKey(WebUser, related_name='createdby')
    total_gst = models.FloatField()
    total_service_charge = models.FloatField()


class Batch(models.Model):
    batch_number = models.CharField(max_length=100)
    card_type= models.CharField(max_length=10, choices=CARD_TYPES)
    card_flavour = models.CharField(max_length=100)
    created_on = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(WebUser, related_name='created_by')
    assigned_to = models.ForeignKey(WebUser, related_name='assigned_to')
    activated = models.BooleanField(default=False)
    purchased = models.BooleanField(default=False)
    total_cost = models.FloatField()
    deleted = models.BooleanField(default=False)
    total_gst = models.FloatField()
    total_service_charge = models.FloatField()
    
    class Meta:
        unique_together = ('batch_number','assigned_to')


class EnumField(models.Field):

    def __init__(self, *args, **kwargs):
        super(EnumField, self).__init__(*args, **kwargs)
        if not self.choices:
            raise AttributeError('EnumField requires `choices` attribute.')

    def db_type(self):
        return "enum(%s)" % ','.join("'%s'" % k for (k, _) in self.choices)


CARD_TYPE1 = 'WLWRTH'
CARD_TYPE2 = 'BLKHWK'
CARD_CHOICES = (
    (CARD_TYPE1, 'WLWRTH'),
    (CARD_TYPE2, 'BLKHWK'),
)


class gift_cards(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=250)
    amount = models.CharField(max_length=250)
    small_image_file = models.CharField(max_length=150)
    upc_code =models.CharField(max_length=50)
    card_type = EnumField(choices=CARD_CHOICES)
    normal_image_file = models.CharField(max_length=150)
    service_charge = models.CharField(max_length=150)
    gst = models.CharField(max_length=150)
    gst_in_commission = models.CharField(max_length=5)
    profit_percentage = models.CharField(max_length=5)
    gst_applicable = models.IntegerField()
    is_deleted = models.IntegerField(max_length=4)
    profit_amount = models.CharField(max_length=5) 	
    class Meta:
       db_table = 'gift_cards'

class GiftCards(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=250)
    amount = models.CharField(max_length=250)
    small_image_file = models.CharField(max_length=150)
    upc_code =models.CharField(max_length=50)
    card_type = models.CharField(max_length=250)
    normal_image_file = models.CharField(max_length=150)
    service_charge = models.CharField(max_length=150)
    gst = models.CharField(max_length=150)
    gst_in_commission = models.CharField(max_length=5)
    profit_percentage = models.CharField(max_length=5)
    gst_applicable = models.IntegerField()
    is_deleted = models.IntegerField(max_length=4)
    profit_amount = models.CharField(max_length=5) 	
    class Meta:
       db_table = 'gift_cards'

class SwipedCard(models.Model):
    card_number = models.CharField( max_length=100)
    card_type = models.CharField(max_length=15)
    card_flavour = models.CharField(max_length=255)
    gift_card_id = models.IntegerField(max_length=25)
    upc_code = models.CharField(max_length=30)
    amount = models.FloatField()
    activated = models.BooleanField(default=False)    
    batch = models.ForeignKey(Batch)
    created_on = models.DateTimeField()
    deleted = models.BooleanField(default=False)
    gst = models.FloatField()
    service_charge = models.FloatField()
    cart_status = models.CharField(max_length=1)    
    def __unicode__(self):
        return self.card_number
