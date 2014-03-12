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
Begin Change Log ***************************************************************
                                                                      
  Itr    Def/Req  Userid      Date       Description
  -----  -------- --------    --------   --------------------------------------
  0.9    339      prashanth  19/01/2014  Added copyright Info
 End Change Log ****************************************************************
'''

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.forms import ModelForm
from django.forms.models import modelformset_factory
#from cards.models import generated_batch, bulk_cards
from cards.models import Batch, SwipedCard
from cards import card_utils
#from utils.card_info import CARD_TYPES
from cards.card_info import CARD_TYPES
from cards.card_info import CARD_FLAVOUR



class SwipedCardForm(ModelForm):
    card_type = forms.ChoiceField(choices=CARD_TYPES)
    card_flavour = forms.ChoiceField(choices=CARD_FLAVOUR)
    #amount = forms.CharField(max_size=2)
    #amount = forms.CharField(widget=forms.TextInput(attrs={'onmouseout':'return validateitems(this);'}))
    #card_flavour = forms.ChoiceField(widget = forms.Select(attrs = {'onclick' : "cardModel(this)"}))
    
    def __init__(self, *args, **kwargs):
        super(SwipedCardForm, self).__init__(*args, **kwargs)                   
        self.fields['card_number'].widget.attrs['autofocus']  = 'on'
        self.fields['amount'].widget.attrs['size'] = 5
        self.fields['amount'].widget.attrs['maxlength'] = 5
   
    class Meta:
        model = SwipedCard
        fields = ['card_type','card_flavour','amount','card_number']

UpdateSetBase = modelformset_factory(
    SwipedCard, extra=0, fields=('card_type','card_flavour','amount','card_number', 'upc_code'))

class UpdateFormSet(UpdateSetBase):
    
    def add_fields(self, form, index):
        super(UpdateFormSet, self).add_fields(form, index)
        form.fields['card_number'].widget.attrs['readonly']  = True 
        #form.fields['is_checked'] = forms.BooleanField(label='Select', required=False)
        form.fields['upc_code'] = forms.CharField(label='UPC / Batch Code', required = True)
        form.fields['card_type'] = forms.ChoiceField(choices=CARD_TYPES)
        form.fields['card_flavour'] = forms.ChoiceField(choices=CARD_FLAVOUR)

   
class UpdateSwipedCardForm(ModelForm):
    card_type = forms.ChoiceField(choices=CARD_TYPES)
    card_flavour = forms.ChoiceField(choices=CARD_FLAVOUR)
    #card_flavour = forms.ChoiceField(widget = forms.Select(attrs = {
     #       'onclick' : "cardModel(this)"}))
    
    def __init__(self, *args, **kwargs):
        super(UpdateSwipedCardForm, self).__init__(*args, **kwargs)                   
        self.fields['card_number'].widget.attrs['readonly']  = True    
    
    class Meta:
        model = SwipedCard
        fields = ['card_type','card_flavour','amount','card_number', 'upc_code']

    #def verify_card_length(self):
    #    if card_type:
    #        length = len(self.cleaned_data.get('card_number'))
    #        if card_type in CARD_TYPES[0] and length == 19:
    #            return True
    #        elif card_type in CARD_TYPES[1] and length == 30:
    #            return True
    #        else:
    #            return False
    #    
 
    #def prepare(self):
    #   
    #    card = self.cleaned_data.get('card_number', None)
    #    card_type = self.cleaned_data.get('card_type', None)
    #    print 'before card split'
    #    if card and card_type:
    #        # for woolworths
    #        print 'coming to card split'
    #        if card_type in CARD_TYPES[0]:
    #            print 'splitting for woolworths'
    #            self['card_number'] = card_utils.woolworth_card_number(card)
    #            self['upc_code']= card_utils.get_woolworth_upc_code(self['card_number'])
    #        elif card_type in CARD_TYPES[1]:
    #            # for blackhawk
    #            self['card_number']= card_utils.blackhawk_card_number(card)
    #            self['upc_code'] = card_utils.get_blackhawk_upc_code(self['card_number'])
    #        else:
    #            print 'card type not found'
    #            return False
    

#class GenerateBulkCardsForm(forms.Form):
#    """
#    A form that generates batch numbers per given range.
#    """
#    batch_number = forms.IntegerField(label=_('Initial batch number'),  required = True)
#    num_cards = forms.IntegerField(label=_('Number of cards'), required = True)
#    cost = forms.IntegerField(label=_('Cost'), required = False)
#    # to be mapped with existing crm vendor list
#    vendors = (
#        ('WLWRTH', 'Woolies'),
#        ('BLKHWK', 'BlackHawk'),
#        ('EPAY', 'EPAY'),
#        )
#    card_type =  forms.ChoiceField(choices=vendors)
#    
#    def save_generated_cards(self, created_by_user):
#        number_of_cards = self.cleaned_data.get('num_cards')
#        cost_per_card = self.cleaned_data.get('cost')
#        new_batch_num = self.cleaned_data.get('batch_number')
#        card_type = self.cleaned_data.get('card_type')
#        print (new_batch_num,cost_per_card)
#        
#        created = card_utils.create_new_batch(number_of_cards,
#                                              cost_per_card,
#                                              new_batch_num,
#                                              card_type, created_by_user)
#       
#
#class EditBulkCardsForm(forms.Form):
#    def __init__(self, *args, **kwargs):
#        extra = kwargs.pop('extra')
#        super(EditBulkCardsForm, self).__init__(*args, **kwargs)
#        if extra !=None:
#            for i, selected in enumerate(extra):
#                card = bulk_cards.objects.get(pk=selected)
#                print card.cost
#                self.fields['c_%s' % selected] = forms.CharField(label=card.card_number,widget=forms.TextInput(attrs={'placeholder': card.cost}))
#        
#
#
#            
            
