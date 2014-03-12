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

select count(card_flavour)  from cards_swipedcard where batch_id=2 group by card_type, card_flavour;


'''
'''
Begin Change Log ***************************************************************
                                                                      
  Itr    Def/Req  Userid      Date       Description
  -----  -------- --------    --------   --------------------------------------
  0.9    339      prashanth  19/01/2014  Added copyright Info
 End Change Log ****************************************************************
'''
# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.context_processors import csrf
from django.contrib.auth import login as dj_login, logout as dj_logout
from django.views.decorators.csrf import csrf_protect
from datetime import datetime
from django.forms.formsets import formset_factory
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

#from cards.forms import GenerateBulkCardsForm, EditBulkCardsForm
from cards.forms import SwipedCardForm, UpdateSwipedCardForm, UpdateFormSet
from cards.models import SwipedCard, Batch, shopcart,gift_cards,EnumField
import card_utils
import tables
from django_tables2 import RequestConfig
from users.models import WebUser
#from cards.models import generated_batch
from django.db.models import Count,Sum
from django.core import serializers
from django.utils import simplejson
from cards.card_utils import verify_card_length



def bulk(request):
    form = SwipedCardForm(request.POST or None)
    response_dict = {'form':form}
    batch_number = request.session.get('batch_number', False)
    card_flv_name = ''
    email = request.user
    msgs=''
    
    if not batch_number:
        batch_number = datetime.now().isoformat()
        try:
            batch = Batch.objects.get(batch_number = batch_number, created_by = email)
        except Batch.DoesNotExist:
            print 'creating new batch %s' % batch_number
            user = WebUser.objects.get(email=email)
            total = 0
            batch = Batch(batch_number = batch_number,
                      created_by = user,
                      assigned_to = user,                      
                      total_cost = total,
                      )
            batch.save()

            request.session['batch_number'] = batch_number

            to_delete_cart = shopcart.objects.filter(activate_card_batch_id=batch.id)
            to_delete_cart.delete()
    else:
             
	batch = Batch.objects.get(batch_number = batch_number)
        if request.method == 'POST':
            ctype = request.POST.get('card_type')
            cnumber = request.POST.get('card_number')
            #print request.POST
            gift_card_id = request.POST.get('cardflavour_dropdown')
            amt = request.POST.get('amount')

            cleaned_card = card_utils.extract_card_number(cnumber,
                                                          ctype)
            if gift_card_id:
                card_flavour = gift_cards.objects.filter(id=gift_card_id)

                for card_flavour_name in card_flavour:
                    card_flv_name = card_flavour_name.name
                    upc_code = card_flavour_name.upc_code
                    check_card_flavor = cnumber.find(upc_code)
                    

            if  ctype and cnumber and amt and gift_card_id:
       
                #print upc_code
                #print check_card_flavor
                
                if check_card_flavor != -1:
                     if verify_card_number(ctype, cleaned_card): 
                          batch1 = SwipedCard(card_number = cleaned_card,
                          card_type = ctype,
                          card_flavour = card_flv_name,
                          gift_card_id = gift_card_id,
                          upc_code = upc_code,
                          amount = amt,
                          batch_id = batch.id,)
                          batch1.save()
                          batch.total_cost = float(batch.total_cost) + float(amt)
                          batch.save()
                          msgs = 'Success'
                     else:
                          msgs = 'Card Number already added!!'
                else:
                	    msgs = 'You have selected %s Flavour, Please select proper card flavour' % card_flv_name          
            else: 
                msgs = 'Please enter all the fields'

            form = SwipedCardForm(initial={'card_type':ctype,
                                           'amount':amt,'card_focus':'on'})
            response_dict.update({'form':form}) 
            
        response_dict.update({'batch_total':batch.total_cost})
        new_cards = SwipedCard.objects.filter(batch_id=batch.id, deleted=False)
        table = tables.SwipedCardTable(new_cards)
        RequestConfig(request,paginate={"per_page": 10}).configure(table)    
        response_dict.update({'table':table,'msgs':msgs,'cflavour':card_flv_name})
    
    return render(request,'web_purchase.html', response_dict)

def verify_card_number(card_type, card_number):
    valid = verify_card_length(card_type, card_number)
    card = SwipedCard.objects.filter(card_number=card_number)
    if len(card) > 0: 
        return False
    else:
        return True


@csrf_exempt
def load_flavours(request):
    response_dict = {}
    flavours_data = []
    card_type = request.POST.get('card_type')
    query = "select id,name,upc_code,small_image_file,card_type from gift_cards where card_type='"+card_type+"'"
    card_flavours = gift_cards.objects.raw(query)
    for flavours in card_flavours:
        flavours_data.append(flavours)
    
    request.session['card_flv'] = flavours_data
    request.session['card_selected'] = card_type
    
    return render(request,'web_purchase.html', response_dict)


def update(request):
    
    if request.method == 'POST':
        selected = request.POST.getlist('selection', None)
        form_set  = SwipedCardForm()
        action = request.POST.get('action')
        response_dict ={'formset':form_set}
        
        if action == 'save':
            formset = UpdateFormSet(request.POST)
            for form in formset.forms:
                submitted = form.save()
                batch_number = request.session['batch_number']
                batch = Batch.objects.get(batch_number = batch_number)
                batch.total_cost = batch.total_cost - submitted.amount
                batch.save()
                
            return HttpResponseRedirect('/cards/bulk/purchase/')
        
        if action == 'delete':
            batch_number = request.session['batch_number']
            batch = Batch.objects.get(batch_number = batch_number)
            form_set = UpdateFormSet(queryset = SwipedCard.objects.filter(pk__in=selected, deleted=False))
            for form in form_set.forms:
                submitted = form.save(commit=False)
                submitted.deleted = True
                submitted.save()
                batch.total_cost = batch.total_cost - submitted.amount
                batch.save()
            response_dict={'batch_total': batch.total_cost}
            return HttpResponseRedirect('/cards/bulk/purchase/', response_dict)

        form_set = UpdateFormSet(queryset = SwipedCard.objects.filter(pk__in=selected, deleted=False))
        response_dict ={'formset':form_set}

    return render(request, 'update_cards.html', response_dict)

def purchase(request):
    if request.method == 'POST':
        pass
        
    return render(request,'purchase.html', response_dict)
    
     
def add_cart(request):
    response_dict = []
    cart_items = []
    shop_cart = []
    card_numbers = []
    if request.session.get('batch_number', False):
        batch_number = request.session.get('batch_number', False)    	
        batch = Batch.objects.get(batch_number = batch_number)
        
        cart_flavours = SwipedCard.objects.values('card_type', 'card_flavour',
                                                  'batch_id','upc_code','gift_card_id').filter(batch_id=batch.id, deleted=False).annotate(Count('card_flavour')).annotate(Sum('amount'))
                
        for c in cart_flavours:                     	
            
            card_number = SwipedCard.objects.values('id','card_number','card_flavour','card_type','batch_id').filter(batch_id=batch.id, card_type=c['card_type'], card_flavour=c['card_flavour'], deleted=False)
            card_numbers.append(card_number)

    resp_dict1 = zip(cart_flavours,response_dict)            	
    createdby_id=request.user

    to_delete_cart = shopcart.objects.filter(activate_card_batch_id=batch.id)
    to_delete_cart.delete()
    
    for cart in cart_flavours:
        gift_card_details = gift_cards.objects.values('id','normal_image_file','service_charge','gst').filter(id=cart['gift_card_id'])
        #.annotate(Sum('service_charge')).annotate(Sum('gst'))
        
        for details in gift_card_details:
            
            if details['normal_image_file']:
                image_name = details['normal_image_file']
            else:
                image_name = 'noImage.png'

            gst_total, service_charge_total = 0,0
            if cart['card_type'] == 'BLKHWK':
                gst_total = cart['card_flavour__count'] * details['gst']
                service_charge_total = cart['card_flavour__count'] * details['service_charge']

            if cart['card_type'] == 'WLWRTH':
                gst_total = cart['card_flavour__count'] * details['gst']
                service_charge_total = cart['card_flavour__count'] * details['service_charge']
                        
            sr = shopcart(card_type = cart['card_type'],gift_card_id=cart['gift_card_id'],card_flavour_image_file=image_name,total_gst=gst_total, total_service_charge=service_charge_total,
        													card_flavour = cart['card_flavour'],
        													activate_card_batch_id = cart['batch_id'], 
        													upc_code=cart['upc_code'],
        													quantity=cart['card_flavour__count'],
        													total_amount = cart['amount__sum'],
        													createdby_id = createdby_id.id)
            sr.save()
            cart_items = shopcart.objects.values('card_flavour',
                                             'total_amount',
					     'card_type','quantity',
                                             'activate_card_batch_id','card_flavour_image_file','total_gst','total_service_charge').filter(activate_card_batch_id = batch.id,card_flavour = cart['card_flavour']).distinct().annotate(Sum('total_gst')).annotate(Sum('total_service_charge'))
            shop_cart.append(cart_items)
    for batch_item in cart_items:
        #print batch_item['activate_card_batch_id']
        batch_update = Batch.objects.get(id=batch_item['activate_card_batch_id'])
        batch_update.total_gst = round(batch_item['total_gst__sum'], 2)
        batch_update.total_service_charge = round(batch_item['total_service_charge__sum'], 2)
        batch_update.save()
    request.session['cartcount'] = len(shop_cart)
    resp_dict = {'cart_items':shop_cart, 'card_numbers':card_numbers}
    
    return render(request,'shopping_cart.html', resp_dict)

    
@csrf_exempt    
def del_cart(request):
    resp_dict = []
    if request.is_ajax():
        ctype = request.POST.get('ctype')  
        cflavour = request.POST.get('cflavour')
        batchid = request.POST.get('batchid')  	
        to_delete_cart = shopcart.objects.filter(card_type=ctype, card_flavour=cflavour, activate_card_batch_id=batchid)
        batch_total = shopcart.objects.values('id','activate_card_batch_id','total_gst','total_service_charge').filter(card_type=ctype, card_flavour=cflavour, activate_card_batch_id=batchid).annotate(Sum('total_amount')).annotate(Sum('total_gst')).annotate(Sum('total_service_charge'))
        for total in batch_total:
        	   success = update_batch_total(total['activate_card_batch_id'],total['total_amount__sum'])
                   gst_success = update_gst_total(total['activate_card_batch_id'],total['total_gst'],total['total_service_charge'])
        	   if success and gst_success:
        	   	    to_delete_cart.delete()
        	   	    to_delete_swiped = SwipedCard.objects.filter(card_type=ctype, card_flavour=cflavour, batch_id=batchid)
        	   	    to_delete_swiped.delete()
        
        cart_count = shopcart.objects.filter(card_type=ctype, card_flavour=cflavour, activate_card_batch_id=batchid)
        resp_dict.append(cart_count)
    resp_dict = {'cart_items':'5'}
    return render(request,'shopping_cart.html', resp_dict)

 	   
def update_batch_total(batch_id,deleted_amount):
	   success = False
	   batch_update = Batch.objects.values('total_cost').filter(id=batch_id)
	   for batch_tot in batch_update:
	   	    new_amount = batch_tot['total_cost'] - deleted_amount
	   	    batch_update_total = Batch.objects.get(id=batch_id)
	   	    batch_update_total.total_cost = new_amount
	   	    batch_update_total.save()
	   	    success = True
	   return success    
     
def update_gst_total(batch_id,gst_total,service_charge_total):
	   success = False
	   batch_update = Batch.objects.values('total_gst','total_service_charge').filter(id=batch_id)
	   for batch_tot in batch_update:
	   	    gst_amount = batch_tot['total_gst'] - gst_total
                    service_charge_amount = batch_tot['total_service_charge'] - service_charge_total
	   	    batch_update_total = Batch.objects.get(id=batch_id)
	   	    batch_update_total.gst_total = gst_amount
                    batch_update_total.service_charge_total = service_charge_amount
	   	    batch_update_total.save()
	   	    success = True
	   return success	 	  
	 	   
def continue_cart(request):
    resp_dict = []	
    return render(request,'purchase.html', response_dict)
           	

