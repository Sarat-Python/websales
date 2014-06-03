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
  Itr         Def/Req    Userid      Date           Description
  -----     --------    --------   --------   ------------------------------
  Sprint3   Story #54   Sarat      30/04/2014     Added Logic for Selection
  of woolies wish cards
 End Change Log ***************************************************************
'''
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.context_processors import csrf
from django.contrib.auth import login as dj_login, logout as dj_logout
from django.views.decorators.csrf import csrf_protect
from datetime import datetime
from django.forms.formsets import formset_factory
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from cards.forms import SwipedCardForm, UpdateSwipedCardForm, UpdateFormSet
from cards.models import SwipedCard, Batch, shopcart, gift_cards, EnumField
import card_utils
from card_utils import extract_cnumber
import tables
from django_tables2 import RequestConfig
from users.models import WebUser
from django.db.models import Count, Sum
from django.core import serializers
from django.utils import simplejson
from cards.card_utils import verify_card_length
from pprint import pprint
from django.core.exceptions import ObjectDoesNotExist

'''
@brief : Method to store swiped cards details based
         on card type and card flavour validations
@param   from_cart is to check if user comes selectes,
         cart is to check if any card selected before card swipe
@return  list of swiped card details in the datatables grid format
'''

@login_required
@csrf_exempt
def bulk(request, cart='', from_cart=''):

    form = SwipedCardForm(request.POST or None)
    response_dict = {'form': form}
    batch_number = request.session.get('batch_number', False)
    card_flv_name = ''
    email = request.user
    gst_total, service_total = 0.00, 0.00
    msgs = ''
    gift_card_id = 0
    is_different = True
    is_new = True
    amount_sum, main_total = 0.00, 0.00

    for i, j in request.session.iteritems():
        print i, j,'--------------session'
    if not batch_number:
        batch_number = datetime.now().isoformat()
        try:
            batch = Batch.objects.get(
                batch_number=batch_number, created_by=email)
        except Batch.DoesNotExist:
            user = WebUser.objects.get(email=email)
            total = 0
            batch = Batch(batch_number=batch_number,
                          created_by=user,
                          assigned_to=user,
                          total_cost=total,
                          )
            batch.save()
            request.session['batch_number'] = batch_number
            request.session['batchid'] = batch.id
            to_delete_cart = shopcart.objects.filter(
                activate_card_batch_id=batch.id)
            to_delete_cart.delete()
    else:

        batch = Batch.objects.get(batch_number=batch_number)
        request.session['batchid'] = batch.id
        wish_gift_card_id = ''
        upc_code_query = ''
        wish_card_number = ''
        gift_card_name = ''

        if cart:
            print 'in one'
            flavours_data = []
            form = SwipedCardForm(request.POST or None)
            response_dict = {'form': form}
            query = "select id,name,upc_code,small_image_file,\
                card_type from gift_cards where card_type='" + cart + "'\
                                                   and is_deleted=0"
            card_flavours = gift_cards.objects.raw(query)
            for flavours in card_flavours:
                flavours_data.append(flavours)
            request.session['card_flv'] = flavours_data
            request.session['card_selected'] = cart

        else:
            print 'in one one'
            request.session['card_selected'] = ''
            request.session['card_flv'] = ''
            request.session['amt'] = ''
            '''
            request.session['card_type'] = ''
            request.session['small_image_file'] = ''
            request.session['upccode'] = ''
            request.session['amount'] = ''
            '''
            
        if from_cart:
            print 'in two'
            c_flavour = gift_cards.objects.filter(id=from_cart)
            for card_flavour_name in c_flavour:
                request.session['selectd_flv_name'] = card_flavour_name.name
                request.session['from_cart'] = from_cart
                request.session['old_upc_code'] = card_flavour_name.upc_code
                if card_flavour_name.card_type == 'WLWRTH':
                    woolworth_amount = SwipedCard.objects.values('amount'
                             ).filter(batch_id=batch.id,gift_card_id=from_cart)
                    for w_amt in woolworth_amount:
                        request.session['amount'] = w_amt['amount']
                else:
                    request.session['amount'] = card_flavour_name.amount
                request.session['link_from'] = 'shopcart'
                request.session['small_image_file'] = card_flavour_name.small_image_file
                request.session['link_id'] = from_cart
                request.session['card_type'] = card_flavour_name.card_type
                request.session['upccode'] = card_flavour_name.upc_code
                #request.session['amount'] = card_flavour_name.upc_code

                
                gift_card_id = from_cart
        
        if request.method == 'POST':
            card_number = request.POST.get('card_number','')
            upccode  = request.POST.get('upc_code','')
            card_type = request.POST.get('card_type', '')
            small_image_file = request.POST.get('small_image_file', '')
            amount = request.POST.get('amount', '')                        
            latest_id = request.POST.get('latest_id','')
            wish_gift_card_id = request.POST.get('wish_gift_card_id','')
            cleaned_card = card_utils.extract_card_number(card_number,card_type)
            upc_code_res = extract_cnumber(card_number)
            request.session['link_from'] = 'addcard'
            card_details = gift_cards.objects.values(
                                                    'id',
                                                    'upc_code',
                                                    'card_type',
                                                    'name',
                                                    'amount',
                                                    'small_image_file',
                                                    'gst',
                                                    'service_charge'
                                                    ).filter(
                                                    upc_code=upc_code_res)
            card_count = card_details.count()
            
            #response_dict.update({'wish_gift_card_id': 'giftcard',})       
            #wish_gift_card_id = 164 
            
            card_type_session = request.session.get('card_type','')
            upccode_session = request.session.get('upccode','')
            small_image_file_session = request.session.get('small_image_file','')
            amount_session = request.session.get('amount','')
            card_number_session = request.session.get('card_number','')
            latest_id = request.session.get('latest_id','')

            if card_type_session and small_image_file_session and amount_session:          
                if card_number_session == cleaned_card:
                    is_new = True
                    is_different = True
                    card_number = request.POST.get('card_number','')
                    check_card_flavor = card_number.find(request.session['upccode'])
                    msgs = 'Card Number aleardy added'
                    #nedd to check to card already added condition
                    
                elif str(upccode) != str(upc_code_res):
                    is_new = True
                    is_different = True
                    card_number = request.POST.get('card_number','')
                    check_card_flavor = card_number.find(request.session['upccode'])
                    msgs = 'Selected Card Flavour does not match with the Card Swiped'
                else:
                    request.session['card_type'] = request.session['card_type']
                    request.session['small_image_file'] = request.session['small_image_file']
                    request.session['upccode'] = request.session['upccode']
                    if request.session['card_type'] == 'WLWRTH':
                        request.session['amount'] = request.POST.get('amount','')
                    elif request.session['card_type'] == 'BLKHWK':
                        request.session['amount'] = request.session['amount']

                    #request.session['latest_id']  = details['id']
                    card_number = request.POST.get('card_number','')
                    request.session['gst'] = request.session['gst']
                    request.session['service_charge'] = request.session['service_charge']
                    check_card_flavor = card_number.find(request.session['upccode'])
                    request.session['card_flavour'] = request.session['card_flavour']
                    request.session['gift_card_id'] = request.session['gift_card_id']                                        
                    is_new = False
                    is_different = False
                    msgs = 'success'
                    
            else:
                is_new = False
                is_different = False
                msgs = 'Success'
                if card_count > 1 and wish_gift_card_id == '':

                    is_new = True
                    is_different = True
                    card_number = request.POST.get('card_number','')
                                                                        
                    for details in card_details:
                        #request.session['card_type'] = details['card_type']
                        #request.session['small_image_file'] = details['small_image_file']
                        request.session['upccode'] = details['upc_code']
                        if details['card_type'] == 'WLWRTH':
                            request.session['amount'] = request.POST.get('amount','')
                        elif details['card_type'] == 'BLKHWK':
                            request.session['amount'] = details['amount']
                        #request.session['latest_id']  = details['id']
                        check_card_flavor = card_number.find(details['upc_code'])
                        #gst = details['gst']
                        #request.session['gst'] = gst
                        #service_charge = details['service_charge']
                        #request.session['service_charge'] = service_charge
                        #request.session['card_flavour'] = details['name']
                        #request.session['gift_card_id'] = details['id']

                        if details['upc_code'] == '628000309':
                            upc_code_query = gift_cards.objects.values('id','small_image_file').filter(
                                    upc_code=details['upc_code'], is_deleted=False)

                    wish_gift_card_id = 'giftcard'
                    wish_card_number = request.POST.get('card_number')

                elif card_count > 1 and wish_gift_card_id:
                    card_details = gift_cards.objects.values(
                                                        'id',
                                                        'upc_code',
                                                        'card_type',
                                                        'name',
                                                        'amount',
                                                        'small_image_file',
                                                        'gst',
                                                        'service_charge'
                                                        ).filter(
                                                        id=wish_gift_card_id)                                      
                    for details in card_details:
                        request.session['card_type'] = details['card_type']
                        request.session['small_image_file'] = details['small_image_file']
                        request.session['upccode'] = details['upc_code']
                        if details['card_type'] == 'WLWRTH':
                            request.session['amount'] = request.POST.get('amount','')
                        elif details['card_type'] == 'BLKHWK':
                            request.session['amount'] = details['amount']
                        request.session['latest_id']  = details['id']
                        check_card_flavor = card_number.find(details['upc_code'])
                        gst = details['gst']
                        request.session['gst'] = gst
                        service_charge = details['service_charge']
                        request.session['service_charge'] = service_charge
                        request.session['card_flavour'] = details['name']
                        request.session['gift_card_id'] = details['id']
                        msgs = 'Success'
                else:
            
                    for details in card_details:
                        request.session['card_type'] = details['card_type']
                        request.session['small_image_file'] = details['small_image_file']
                        request.session['upccode'] = details['upc_code']
                        if details['card_type'] == 'WLWRTH':
                            request.session['amount'] = request.POST.get('amount','')
                        elif details['card_type'] == 'BLKHWK':
                            request.session['amount'] = details['amount']

                        request.session['latest_id']  = details['id']
                        check_card_flavor = card_number.find(details['upc_code'])
                        gst = details['gst']
                        request.session['gst'] = gst
                        service_charge = details['service_charge']
                        request.session['service_charge'] = service_charge
                        request.session['card_flavour'] = details['name']
                        request.session['gift_card_id'] = details['id']              
                
            card_number = request.POST.get('card_number','')
            card_type = request.session.get('card_type','')
            cleaned_card = card_utils.extract_card_number(card_number,card_type)

            if check_card_flavor != -1 and is_new is False and is_different is False:
                if verify_card_number(request.session['card_type'], cleaned_card):
                    if card_type != "BLKHWK":
                        request.session['gst'] = 0
                    else:
                        request.session['gst'] = request.session['gst']
                    batch1 = SwipedCard(card_number=cleaned_card,
                                        card_type=request.session['card_type'],
                                        card_flavour=request.session['card_flavour'],
                                        gift_card_id=request.session['gift_card_id'],
                                        upc_code=request.session['upccode'],
                                        amount=request.session['amount'],
                                        gst=request.session['gst'],
                                        service_charge=request.session['service_charge'],
                                        cart_status=0,
                                        batch_id=batch.id)
                    batch1.save()
                    batch.total_cost = float(batch.total_cost) + float(request.session['amount'])
                    batch.save()
                    request.session['old_upc_code'] = request.session['upccode']
                    request.session['link_id'] = gift_card_id
                    msgs = 'Success'
                    wish_card_number = ''
                    wish_gift_card_id = ''
                else:
                    msgs = 'Card Number already added!!'
                    wish_card_number = ''
                    wish_gift_card_id = ''

            
            form = SwipedCardForm(initial={'card_type': card_type,
                                           'amount': amount, 'card_focus': 'on'})
            response_dict.update({'form': form,
                                  'card_count': card_count,
                                  'wish_card_number': wish_card_number,
                                  'card_details': card_details,
                                  'gift_card_id': gift_card_id,
                                  'wish_gift_card_id': wish_gift_card_id,
                                  'upc_code_query': upc_code_query})

        cart_status_id = [0, 1]

        if cart:
            if from_cart:
                gift_card_id = from_cart
                request.session['amt_new'] = request.session['amt']

            upc_code = gift_cards.objects.values(
                'id', 'upc_code').filter(id=gift_card_id)
            for w_g_c in upc_code:
                gift_card_name = w_g_c['upc_code']
                
            charge_list = SwipedCard.objects.values(
                                                'id',
                                                'cart_status').filter(
                                                batch_id=batch.id).filter(
                                                cart_status__in=cart_status_id,
                                                upc_code=gift_card_name
                                                ).annotate(
                                                Sum('gst')).annotate(
                                                Sum('service_charge')
                                                ).annotate(Sum('amount'))

        else:
            cart_flag = 0
            charge_list = SwipedCard.objects.values(
                                                'id',
                                                'cart_status').filter(
                                                batch_id=batch.id).filter(
                                                cart_status=cart_flag).annotate(
                                                Sum('gst')).annotate(
                                                Sum('service_charge')
                                                ).annotate(Sum('amount'))

        if charge_list and cart:
            other_totals = reduce(sum_dict, charge_list)
            gst_total = other_totals['gst__sum']
            service_total = other_totals['service_charge__sum']
            amount_sum = other_totals['amount__sum']
            gst_total = 0
            main_total = amount_sum + gst_total + service_total
            upc_code = gift_cards.objects.values(
                'id', 'upc_code').filter(id=gift_card_id)
            for w_g_c in upc_code:
                gift_card_name = w_g_c['upc_code']

            new_cards = SwipedCard.objects.filter(
                cart_status__in=cart_status_id).filter(
                batch_id=batch.id,
                deleted=False, upc_code=gift_card_name)

            response_dict.update({'batch_total': amount_sum,
                                  'gst_total': gst_total,
                                  'main_total': main_total,
                                  'service_charge_total': service_total})

        elif charge_list:
            other_totals = reduce(sum_dict, charge_list)
            gst_total = other_totals['gst__sum']
            service_total = other_totals['service_charge__sum']
            amount_sum = other_totals['amount__sum']
            gst_total = 0
            main_total = amount_sum + gst_total + service_total
            new_cards = SwipedCard.objects.filter(
                                                batch_id=batch.id,
                                                deleted=False,
                                                cart_status=cart_flag)
            response_dict.update({'batch_total': amount_sum,
                                  'gst_total': gst_total,
                                  'main_total': main_total,
                                  'service_charge_total': service_total})
        else:

            new_cards = SwipedCard.objects.filter(batch_id=batch.id,
                                                  deleted=False, cart_status=0)
            response_dict.update({'batch_total': batch.total_cost})

        table = tables.SwipedCardTable(new_cards)
        cards_count = new_cards.count()
        RequestConfig(request, paginate={"per_page": 10}).configure(table)
        response_dict.update({'table': table,
                              'msgs': msgs,
                              'cflavour': card_flv_name,
                              'gift_card_id': gift_card_id})
    request.session['total_amount'] = ''
    request.session['main_total'] = ''
    request.session['gst_total'] = ''
    request.session['service_charge_total'] = ''
    request.session['total_amount'] = amount_sum
    request.session['main_total'] = main_total
    request.session['gst_total'] = gst_total
    request.session['service_charge_total'] = service_total
    request.session['card_items_count'] = ''
    if from_cart == '':
        request.session['amt_new'] = ''
    
    try:
        latest_insert_id = SwipedCard.objects.latest('id')
        request.session['latest_insert_id'] = latest_insert_id.gift_card_id
    except: 
        request.session['latest_insert_id'] = ''                                                
    return render(request, 'web_purchase.html', response_dict)

'''
@brief : Method to accept two dict and returns sum of each elements
@param   d1, d2 are the two input dict
@return  sum of the final dic     
'''


def sum_dict(d1, d2):
    for key, value in d1.items():
        d1[key] = value + d2.get(key, 0)
    return d1


'''
@brief : Method to verify swiped card info if already exists
@param   card_number, card_type from swiped card
@return  sum of the final dict     
'''


def verify_card_number(card_type, card_number):
    valid = verify_card_length(card_type, card_number)
    card = SwipedCard.objects.filter(card_number=card_number)
    if len(card) > 0:
        return False
    else:
        return True


'''
@brief : Method to load card flavour details in to the add cart form
@return  card flavour details     
'''


@login_required
@csrf_exempt
def load_flavours(request, card_type=''):
    #response_dict = {}
    flavours_data = []
    form = SwipedCardForm(request.POST or None)
    response_dict = {'form': form}

    query = "select id,name,upc_code,small_image_file,\
                card_type from gift_cards where card_type='" + card_type + "'"
    card_flavours = gift_cards.objects.raw(query)
    for flavours in card_flavours:
        flavours_data.append(flavours)

    request.session['card_flv'] = flavours_data
    request.session['card_selected'] = card_type

    return render(request, 'web_purchase.html', response_dict)


'''
@brief : Method to update swiped card details,
         For deleting swiped cards data

@return  returns updated list of swiped card details    
'''


@login_required
@csrf_exempt
def update(request, ctype=''):
    for_cart = request.POST.get('for_cart')
    action = request.POST.get('action')
    swiped_count = request.POST.get('swiped_count')
    if request.method == 'POST':
        form_set = SwipedCardForm(request.POST or None)
        action = request.POST.get('action')
        form_count = request.POST.get('form-TOTAL_FORMS')
        form_count = int(0 if form_count is None else form_count)
        selected = request.POST.getlist('selection', None)

        if action == 'updatecart':
            batchid = request.POST.get('batchid')
            ctype = request.POST.get('ctype')
            cflavour = request.POST.get('cflavour')
            swiped_snos = SwipedCard.objects.values('id').filter(
                batch_id=batchid, card_type=ctype,
                card_flavour=cflavour)
            global selected
            selected = formatList(swiped_snos)

        if form_count != 0 and action == 'save':
            for i in range(0, form_count):
                form_name = 'form-' + str(i) + '-amount'
                form_id = 'form-' + str(i) + '-id'
                amount = request.POST.get(form_name)
                valid = request.POST.get(form_id)
                update = SwipedCard.objects.get(id=valid)
                update.amount = amount
                update.save()
                #request.session['card_items_count'] = SwipedCard.objects.count()
                # if request.session['amt'] != 0:
                #    request.session['amtdel'] = request.session['amt']
                gift_card_ids = SwipedCard.objects.values(
                    'gift_card_id').filter(
                    id=valid)

                for gift_card_id in gift_card_ids:
                    gift_card_id = gift_card_id['gift_card_id']
                    request.session['link_from'] = 'update'
                    gift_card_id = str(gift_card_id)

            return HttpResponseRedirect(
                                '/cards/bulk/' + request.session['card_type'] + '/' + gift_card_id + '/')

        if action == 'delete':

            batch_number = request.session['batch_number']
            batch = Batch.objects.get(batch_number=batch_number)
            form_set = UpdateFormSet(queryset=SwipedCard.objects.filter(
                pk__in=selected, deleted=False))
            for form in form_set.forms:
                submitted = form.save(commit=False)
                submitted.deleted = True
                submitted.save()
                batch.total_cost = batch.total_cost - submitted.amount
                batch.save()
                gift_card_ids = SwipedCard.objects.values(
                    'gift_card_id').filter(
                    id__in=selected)

                for gift_card_id in gift_card_ids:
                    gift_card_id = gift_card_id['gift_card_id']

                del_cards = SwipedCard.objects.filter(id__in=selected)
                del_cards.delete()

                if swiped_count == '0':
                    request.session['card_type'] = ''
                    request.session['small_image_file'] = ''
                    request.session['upccode'] = ''
                    request.session['amount'] = ''                
                    #request.session['card_selected'] = ''
                    #request.session['small_image_file'] = ''
                    #request.session['amt'] = ''
                    #request.session['amt_new'] = request.session['amt']
                else:
                    if request.session['amt'] != 0:
                        request.session['card_type'] = request.session['card_type']
                        request.session['small_image_file'] = request.session['small_image_file']
                        request.session['upccode'] = request.session['upccode']
                        request.session['amount'] = request.session['amount']

                #request.session['card_items_count'] = swiped_count
                # if request.session['amt'] != 0:
                #    request.session['amtdel'] = request.session['amt']
                gift_card_id = str(gift_card_id)

                if swiped_count == '0':
                    redirect_url = '/cards/bulk/purchase/'
                else:
                    redirect_url = '/cards/bulk/' + \
                        request.session['card_type'] + \
                        '/' + gift_card_id + '/'

                request.session['link_from'] = 'delete'
            return HttpResponseRedirect(redirect_url)

    form_set = UpdateFormSet(queryset=SwipedCard.objects.filter(
        pk__in=selected, deleted=False))
    response_dict = {'formset': form_set}

    return render(request, 'update_cards.html', response_dict)


'''
@brief : Method to format the selected ids into list 
         from updating fucntionality from car page

@return  list of the formatted selected list
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

    return render(request, 'purchase.html', response_dict)


'''
@brief : Method to add items in to cart order page from swiped card list 
         by grouping batchid, card flavour and card type

@return  redirets to shop cart page
'''


@login_required(login_url='/')
def add_cart(request):
    response_dict = []
    cart_items = []
    shop_cart = []
    card_numbers = []
    total_amount, gst_total, service_total = 0.00, 0.00, 0.00
    request.session['selectd_flv_name'] = ''
    
    request.session['card_type'] = ''
    request.session['small_image_file'] = ''
    request.session['upccode'] = ''
    request.session['amount'] = ''
        
    if request.session.get('batch_number', False):
        batch_number = request.session.get('batch_number', False)
        batch = Batch.objects.get(batch_number=batch_number)
        cart_flavours = SwipedCard.objects.values('card_type', 'card_flavour',
                                                  'batch_id', 'upc_code', 'gift_card_id').filter(
            batch_id=batch.id,
            deleted=False).exclude(cart_status='2').annotate(
            Count('card_flavour')).annotate(Sum('amount'))

        for c in cart_flavours:
            card_number = SwipedCard.objects.values('id', 'card_number',
                                                    'card_flavour', 'card_type', 'batch_id').filter(
                batch_id=batch.id, card_type=c['card_type'],
                card_flavour=c['card_flavour'], deleted=False)
            card_numbers.append(card_number)

    resp_dict1 = zip(cart_flavours, response_dict)
    createdby_id = request.user

    to_delete_cart = shopcart.objects.filter(activate_card_batch_id=batch.id)
    to_delete_cart.delete()

    for cart in cart_flavours:
        gift_card_details = gift_cards.objects.values('id', 'small_image_file',
                                                      'service_charge', 'gst').filter(
            id=cart['gift_card_id'])
        for details in gift_card_details:
            if details['small_image_file']:
                image_name = details['small_image_file']
            else:
                image_name = 'noImage.png'

            gst_total, service_charge_total = 0, 0
            if cart['card_type'] == 'BLKHWK':
                gst_total = cart['card_flavour__count'] * details['gst']
                service_charge_total = cart['card_flavour__count'] * details[
                    'service_charge']

            if cart['card_type'] == 'WLWRTH':
                #gst_total = cart['card_flavour__count'] * details['gst']
                gst_total = 0
                service_charge_total = cart['card_flavour__count'] * details[
                    'service_charge']

            sr = shopcart(card_type=cart['card_type'],
                        gift_card_id=cart['gift_card_id'],
                        card_flavour_image_file=image_name,
                        total_gst=gst_total,
                        total_service_charge=service_charge_total,
                        card_flavour=cart['card_flavour'],
                        activate_card_batch_id=cart['batch_id'],
                        upc_code=cart['upc_code'],
                        quantity=cart['card_flavour__count'],
                        total_amount=cart['amount__sum'],
                        createdby_id=createdby_id.id)
            sr.save()

            cart_flag = SwipedCard.objects.values('id', 'cart_status').filter(batch_id=batch.id)
            for flag in cart_flag:
                flag = SwipedCard.objects.filter(
                    id=flag['id']).exclude(cart_status='2')
                for cs in flag:
                    cs.cart_status = 1
                    cs.save()
                request.session['card_flv'] = ''
                request.session['card_selected'] = ''

            cart_items = shopcart.objects.values('card_flavour',
                                                'total_amount',
                                                'card_type', 'quantity',
                                                'activate_card_batch_id',
                                                'card_flavour_image_file',
                                                'total_gst', 'gift_card_id',
                                                'total_service_charge').filter(
                                                activate_card_batch_id=batch.id,
                                                card_flavour=cart['card_flavour']).distinct().annotate(
                                                Sum('total_gst')).annotate(
                                                Sum('total_service_charge'
                                                )).annotate(Sum('total_amount'))
            shop_cart.append(cart_items)

    for batch_item in cart_items:
        batch_update = Batch.objects.get(id=batch_item['activate_card_batch_id'])
        batch_update.total_gst = round(batch_item['total_gst__sum'], 2)
        batch_update.total_service_charge = round(
            batch_item['total_service_charge__sum'], 2)
        batch_update.save()
    request.session['cartcount'] = len(shop_cart)

    charge_list = shopcart.objects.values('id').filter(
        activate_card_batch_id=batch.id).annotate(
        Sum('total_amount')).annotate(
        Sum('total_gst')).annotate(
        Sum('total_service_charge'))
    if charge_list:
        other_totals = reduce(sum_dict, charge_list)
        gst_total = other_totals['total_gst__sum']
        total_amount = other_totals['total_amount__sum']
        service_total = other_totals['total_service_charge__sum']
        gst_total = 0
        main_total = total_amount + gst_total + service_total
        resp_dict = {'cart_items': shop_cart, 'card_numbers': card_numbers,
                     'batch_total': total_amount, 'gst_total': gst_total,
                     'service_charge_total': service_total,
                     'main_total': main_total}
    else:
        resp_dict = {'cart_items': shop_cart,
                     'card_numbers': card_numbers,
                     'total_amount': total_amount}

    return render(request, 'shopping_cart.html', resp_dict)


'''
@brief : Method to add items in to cart order page from swiped card list 
         by grouping batchid, card flavour and card type

@return  redirets to shop cart page
'''


@login_required(login_url='/')
def goto_cart(request):
    response_dict = []
    cart_items = []
    shop_cart = []
    card_numbers = []
    total_amount, gst_total, service_total = 0.00, 0.00, 0.00
    request.session['selectd_flv_name'] = ''
    if request.session.get('batch_number', False):
        batch_number = request.session.get('batch_number', False)
        batch = Batch.objects.get(batch_number=batch_number)
        cart_flavours = SwipedCard.objects.values('card_type', 'card_flavour',
                                                  'batch_id', 'upc_code', 'gift_card_id').filter(
            batch_id=batch.id,
            deleted=False, cart_status=1).annotate(
            Count('card_flavour')).annotate(Sum('amount'))
        for c in cart_flavours:
            card_number = SwipedCard.objects.values('id', 'card_number',
                                                    'card_flavour', 'card_type', 'batch_id').filter(
                batch_id=batch.id,
                card_type=c['card_type'],
                card_flavour=c['card_flavour'],
                deleted=False, cart_status=1)
            card_numbers.append(card_number)

    resp_dict1 = zip(cart_flavours, response_dict)
    createdby_id = request.user

    to_delete_cart = shopcart.objects.filter(activate_card_batch_id=batch.id)
    to_delete_cart.delete()

    for cart in cart_flavours:
        gift_card_details = gift_cards.objects.values('id', 'small_image_file',
                                                      'service_charge', 'gst').filter(
            id=cart['gift_card_id'])
        for details in gift_card_details:
            if details['small_image_file']:
                image_name = details['small_image_file']
            else:
                image_name = 'noImage.png'

            gst_total, service_charge_total = 0, 0
            if cart['card_type'] == 'BLKHWK':
                gst_total = cart['card_flavour__count'] * details['gst']
                service_charge_total = cart['card_flavour__count'] * details[
                    'service_charge']

            if cart['card_type'] == 'WLWRTH':
                #gst_total = cart['card_flavour__count'] * details['gst']
                gst_total = 0
                service_charge_total = cart['card_flavour__count'] * details[
                    'service_charge']

            sr = shopcart(card_type=cart['card_type'], gift_card_id=cart[
                'gift_card_id'], card_flavour_image_file=image_name,
                total_gst=gst_total,
                total_service_charge=service_charge_total,
                card_flavour=cart['card_flavour'],
                activate_card_batch_id=cart['batch_id'],
                upc_code=cart['upc_code'],
                quantity=cart['card_flavour__count'],
                total_amount=cart['amount__sum'],
                createdby_id=createdby_id.id)
            sr.save()

            cart_flag = SwipedCard.objects.values('id', 'cart_status'
                                                  ).filter(batch_id=batch.id)
            for flag in cart_flag:
                request.session['card_flv'] = ''
                request.session['card_selected'] = ''

            cart_items = shopcart.objects.values('card_flavour',
                                                 'total_amount',
                                                 'card_type', 'quantity',
                                                 'activate_card_batch_id',
                                                 'card_flavour_image_file',
                                                 'total_gst', 'gift_card_id',
                                                 'total_service_charge').filter(
                activate_card_batch_id=batch.id,
                card_flavour=cart['card_flavour'
                                  ]).distinct().annotate(
                Sum('total_gst')).annotate(
                Sum('total_service_charge'
                    )).annotate(Sum('total_amount'))
            shop_cart.append(cart_items)

    for batch_item in cart_items:
        batch_update = Batch.objects.get(
            id=batch_item['activate_card_batch_id'])
        batch_update.total_gst = round(batch_item['total_gst__sum'], 2)
        batch_update.total_service_charge = round(
            batch_item['total_service_charge__sum'], 2)
        batch_update.save()
    request.session['cartcount'] = len(shop_cart)

    charge_list = shopcart.objects.values('id').filter(
        activate_card_batch_id=batch.id).annotate(
        Sum('total_amount')).annotate(
        Sum('total_gst')).annotate(
        Sum('total_service_charge'))
    if charge_list:
        other_totals = reduce(sum_dict, charge_list)
        gst_total = other_totals['total_gst__sum']
        total_amount = other_totals['total_amount__sum']
        service_total = other_totals['total_service_charge__sum']
        gst_total = 0
        main_total = total_amount + gst_total + service_total
        resp_dict = {'cart_items': shop_cart, 'card_numbers': card_numbers,
                     'batch_total': total_amount, 'gst_total': gst_total,
                     'service_charge_total': service_total,
                     'main_total': main_total}
    else:
        resp_dict = {'cart_items': shop_cart,
                     'card_numbers': card_numbers,
                     'total_amount': total_amount}

    return render(request, 'shopping_cart.html', resp_dict)


'''
@brief : to delete swiped card items from cart order page
@return  redirets to updated shop cart page
'''


@login_required
@csrf_exempt
def del_cart(request):
    resp_dict = []
    if request.is_ajax():
        ctype = request.POST.get('ctype')
        cflavour = request.POST.get('cflavour')
        batchid = request.POST.get('batchid')
        to_delete_cart = shopcart.objects.filter(
            card_type=ctype,
            card_flavour=cflavour,
            activate_card_batch_id=batchid)
        batch_total = shopcart.objects.values('id', 'activate_card_batch_id',
                                              'total_gst', 'total_service_charge'
                                              ).filter(card_type=ctype,
                                                       card_flavour=cflavour,
                                                       activate_card_batch_id=batchid
                                                       ).annotate(Sum('total_amount')).annotate(
            Sum('total_gst')).annotate(
            Sum('total_service_charge'))
        for total in batch_total:
            success = update_batch_total(total['activate_card_batch_id'],
                                         total['total_amount__sum'])
            gst_success = update_gst_total(
                total['activate_card_batch_id'],
                total['total_gst'],
                total['total_service_charge'])
            if success and gst_success:
                to_delete_cart.delete()
                to_delete_swiped = SwipedCard.objects.filter(
                    card_type=ctype,
                    card_flavour=cflavour,
                    batch_id=batchid)
                to_delete_swiped.delete()

        cart_count = shopcart.objects.filter(card_type=ctype,
                                             card_flavour=cflavour,
                                             activate_card_batch_id=batchid)
        resp_dict.append(cart_count)
    resp_dict = {'cart_items': '5'}
    return render(request, 'shopping_cart.html', resp_dict)


'''
@brief : Batch total updating when bulk update & delete events occurs
@params : batch id, amount for deleted items
@return  success status after batch total update.
'''


def update_batch_total(batch_id, deleted_amount):
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
@brief : Common function to calculate gst and service charge 
details on cart order page
@params : batch_id,gst_total,service_charge_total
@return  returns status after updating gst & service charge total.
'''


def update_gst_total(batch_id, gst_total, service_charge_total):
    success = False
    batch_update = Batch.objects.values('total_gst',
                                        'total_service_charge').filter(
        id=batch_id)
    for batch_tot in batch_update:
        gst_amount = batch_tot['total_gst'] - gst_total
        service_charge_amount = batch_tot['total_service_charge']\
            - service_charge_total
        batch_update_total = Batch.objects.get(id=batch_id)
        batch_update_total.gst_total = gst_amount
        batch_update_total.service_charge_total = service_charge_amount
        batch_update_total.save()
        success = True
    return success


@login_required
def continue_cart(request):
    resp_dict = []
    return render(request, 'purchase.html', response_dict)
    
