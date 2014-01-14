from django.db import models
from django.utils import timezone
from users.models import WebUser
from cards.card_utils import verify_card_length
from cards.card_info import CARD_TYPES
# Create your models here.

class Batch(models.Model):
    batch_number = models.CharField(max_length=100)
    card_type= models.CharField(max_length=10, choices=CARD_TYPES)
    created_on = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(WebUser, related_name='created_by')
    assigned_to = models.ForeignKey(WebUser, related_name='assigned_to')
    activated = models.BooleanField(default=False)
    purchased = models.BooleanField(default=False)
    total_cost = models.FloatField()
    deleted = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('batch_number','assigned_to')
        

#
#class bulk_cards(models.Model):
#    card_number = models.IntegerField(unique = True)
#    card_type= models.CharField(max_length=10)
#    batch = models.ForeignKey(generated_batch)
#    cost = models.FloatField()
#    active_status = models.BooleanField(default=False)
#    class Meta:
#        unique_together = ('card_number', 'card_type',)

class SwipedCard(models.Model):
    card_number = models.CharField( max_length=100)
    # change here to accomodate lenghtier card type names
    card_type = models.CharField(max_length=15)
    upc_code = models.CharField(max_length=30)
    amount = models.FloatField()
    activated = models.BooleanField(default=False)    
    batch = models.ForeignKey(Batch)
    created_on = models.DateTimeField(default=timezone.now)
    deleted = models.BooleanField(default=False)
    def __unicode__(self):
        return self.card_number
    
    def verify_card_number(self):
        card_type = self.card_type
        card_number = self.card_number
        valid = verify_card_length(card_type, card_number)
        return valid
    
    

    