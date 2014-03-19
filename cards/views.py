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
Begin Change Log **************************************************************************
                                                                      
  Itr        Def/Req               Userid      Date           Description
  -----     --------               --------  --------       -------------------------------
  Sprint     Bug 8,9,10,11,12      NaveeN    19/03/2014       Added Shopcart Functionality
 End Change Log ***************************************************************************
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
from pprint import pprint

'''
 Function to create Batch id, when user log in and to store swiped cards information 
'''

def bulk(request):
    form = SwipedCardForm(request.POST or None)
    response_dict = {'form':form}
    batch_number = request.session.get('batch_number', False)
    card_flv_name = ''
    email = request.user
    gst_total, service_total = 0.00, 0.00		
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
            request.session['batchid'] = batch.id

            to_delete_cart = shopcart.objects.filter(activate_card_batch_id=batch.id)
            to_delete_cart.delete()
    else:
             
	batch = Batch.objects.get(batch_number = batch_number)
	request.session['batchid'] = batch.id
        if request.method == 'POST':
            ctype = request.POST.get('card_type')
            cnumber = request.POST.get('card_number')
            gift_card_id = request.POST.get('cardflavour_dropdown')
            amt = request.POST.get('amount')

            cleaned_card = card_utils.extract_card_number(cnumber,
                                                          ctype)
            if gift_card_id:
                card_flavour = gift_cards.objects.filter(id=gift_card_id)

                for card_flavour_name in card_flavour:
                    card_flv_name = card_flavour_name.name
                    upc_code = card_flavour_name.upc_code
                    gst = card_flavour_name.gst
                    service_charge = card_flavour_name.service_charge
                    check_card_flavor = cnumber.find(upc_code)
                    

            if  ctype and cnumber and amt and gift_card_id:
                
                if check_card_flavor != -1:
                     if verify_card_number(ctype, cleaned_card): 
                          batch1 = SwipedCard(card_number = cleaned_card,
                          card_type = ctype,
                          card_flavour = card_flv_name,
                          gift_card_id = gift_card_id,
                          upc_code = upc_code,
                          amount = amt,
                          gst = gst, service_charge=service_charge,cart_status=0,    						  
                          batch_id = batch.id)
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

            
        			
        charge_list = SwipedCard.objects.values('id','cart_status').filter(batch_id=batch.id).filter(cart_status=0).annotate(Sum('gst')).annotate(Sum('service_charge')).annotate(Sum('amount'))
        if charge_list:
            other_totals = reduce(sum_dict, charge_list)
            gst_total = other_totals['gst__sum']
            service_total = other_totals['service_charge__sum']
            amount_sum = other_totals['amount__sum']
            main_total = amount_sum + gst_total + service_total
            new_cards = SwipedCard.objects.filter(batch_id=batch.id, deleted=False,cart_status=0)
             
            response_dict.update({'batch_total':amount_sum,'gst_total':gst_total,'main_total': main_total, 'service_charge_total': service_total})
        else:
            
            new_cards = SwipedCard.objects.filter(batch_id=batch.id, deleted=False, cart_status=0)
            response_dict.update({'batch_total':batch.total_cost})
        
        table = tables.SwipedCardTable(new_cards)
        RequestConfig(request,paginate={"per_page": 10}).configure(table)    
        response_dict.update({'table':table,'msgs':msgs,'cflavour':card_flv_name})
    
    return render(request,'web_purchase.html', response_dict)

'''
 Common Method to calculate sum for the given list
'''
def sum_dict(d1, d2):
    for key, value in d1.items():
        d1[key] = value + d2.get(key, 0)
    return d1
	
'''
 verify_card_number(card_type, card_number): to verify swiped card info is already exists
'''	
def verify_card_number(card_type, card_number):
    valid = verify_card_length(card_type, card_number)
    card = SwipedCard.objects.filter(card_number=card_number)
    if len(card) > 0: 
        return False
    else:
        return True

'''
 Populate card flavour data to swiped card form
'''
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


'''
 update(request): 1. for bulk updating swiped cards info
 2. For deleting swiped cards data
 3. Update option from cart order page
'''
@csrf_exempt
def update(request):
    for_cart = request.POST.get('for_cart')
    action = request.POST.get('action')
    #selected = [u'152', u'153', u'154', u'155', u'156', u'157', u'158', u'159']
    if request.method == 'POST':
    	   form_set  = SwipedCardForm(request.POST or None)
    	   action = request.POST.get('action')
    	   form_count = request.POST.get('form-TOTAL_FORMS')
    	   form_count = int(0 if form_count is None else form_count)
    	   selected = request.POST.getlist('selection', None)
    	   	   
    	   if action == 'updatecart':
    	   	   batchid = request.POST.get('batchid')
    	   	   ctype = request.POST.get('ctype')
    	   	   cflavour = request.POST.get('cflavour')
    	   	   swiped_snos = SwipedCard.objects.values('id').filter(batch_id=batchid, card_type=ctype, card_flavour=cflavour)
    	   	   global selected
    	   	   selected = formatList(swiped_snos)
 	   	   
    	   if form_count != 0 and action == 'save':
    	   	   for i in range(0, form_count):
    	   	   	    form_name = 'form-'+str(i)+'-amount'
    	   	   	    form_id = 'form-'+str(i)+'-id'
    	   	   	    amount = request.POST.get(form_name)
    	   	   	    valid = request.POST.get(form_id)
    	   	   	    update = SwipedCard.objects.get(id=valid)
    	   	   	    update.amount = amount
    	   	   	    update.save()
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
        	   	   del_cards = SwipedCard.objects.filter(id__in=selected)
        	   	   del_cards.delete()
        	   return HttpResponseRedirect('/cards/bulk/purchase/')
     	   
    form_set = UpdateFormSet(queryset = SwipedCard.objects.filter(pk__in=selected, deleted=False))
    response_dict ={'formset':form_set}

    return render(request, 'update_cards.html', response_dict)
 
'''
  Used to fetch selected id details for updating from cart order page
   
'''
def formatList(cartList):
    snos = []
    for k in cartList:
      	 snos.append(k['id'])
    cart_selected = [unicode(i) for i in snos]
    return cart_selected

   
def purchase(request):
    if request.method == 'POST':
        pass
        
    return render(request,'purchase.html', response_dict)
    
'''
 Common function to add items in to cart order based on grouping of card type, card flavour and batch id
'''     
def add_cart(request):
    response_dict = []
    cart_items = []
    shop_cart = []
    card_numbers = []
    total_amount, gst_total, service_total = 0.00, 0.00, 0.00
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

            cart_flag = SwipedCard.objects.values('id','cart_status').filter(batch_id=batch.id)
            for flag in cart_flag:
                #print flag['id']
	        flag = SwipedCard.objects.get(id=flag['id'])
                flag.cart_status = 1
                flag.save()
                request.session['card_flv'] = ''
                request.session['card_selected'] = ''
	
            cart_items = shopcart.objects.values('card_flavour',
                                             'total_amount',
					     'card_type','quantity',
                                             'activate_card_batch_id','card_flavour_image_file','total_gst','total_service_charge').filter(activate_card_batch_id = batch.id,card_flavour = cart['card_flavour']).distinct().annotate(Sum('total_gst')).annotate(Sum('total_service_charge')).annotate(Sum('total_amount'))
            shop_cart.append(cart_items)
    
    for batch_item in cart_items:
        batch_update = Batch.objects.get(id=batch_item['activate_card_batch_id'])
        batch_update.total_gst = round(batch_item['total_gst__sum'], 2)
        batch_update.total_service_charge = round(batch_item['total_service_charge__sum'], 2)
        batch_update.save()
    request.session['cartcount'] = len(shop_cart)

    charge_list = shopcart.objects.values('id').filter(activate_card_batch_id=batch.id).annotate(Sum('total_amount')).annotate(Sum('total_gst')).annotate(Sum('total_service_charge'))
    if charge_list:
        other_totals = reduce(sum_dict, charge_list)
        gst_total = other_totals['total_gst__sum']
        total_amount = other_totals['total_amount__sum']
        service_total = other_totals['total_service_charge__sum']
        main_total = total_amount + gst_total + service_total
        resp_dict = {'cart_items':shop_cart, 'card_numbers':card_numbers,'batch_total':total_amount, 'gst_total':gst_total, 'service_charge_total':service_total, 'main_total':main_total}
    else:
        resp_dict = {'cart_items':shop_cart, 'card_numbers':card_numbers,'total_amount':total_amount}
    
    return render(request,'shopping_cart.html', resp_dict)

'''
 Common Delete function to delete swiped card items and cart order page
'''    
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

'''
  Batch total updating when bulk update & delete events occurs
''' 	   
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
     
'''
 Common function to calculate gst and service charge details on cart order page
'''     
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
           	

