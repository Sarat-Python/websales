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
                                                                      
  Itr       Def/Req         Userid        Date                Description
  -----     --------      --------      --------      -------------------------
  Sprint 3    Story#21      Sarat       04/04/2014     Added Functions to
                                                       extract Card Type,Card
                                                       Flavour and Upc Code
                                                       from Card Number
 End Change Log ***************************************************************
'''

#from cards.models import generated_batch, bulk_cards
from card_info import CARD_TYPES

#def clean_save_card():

def extract_upc_code(cnumber,ctype):
     if cnumber != None :
        if ctype =='WLWRTH':
            return get_woolworth_upc_code(cnumber)
        elif ctype =='BLKHWK':
            return get_blackhawk_upc_code(cnumber)
        else:
            return get_woolworth_upc_code(cnumber)


def woolworth_card_number(swipe_data):
  card_number = swipe_data[1:swipe_data.find('=')]
  print 'processed %s' % card_number 
  return card_number;

def blackhawk_card_number(swipe_data):
    number_extract = swipe_data[2:swipe_data.find(' ')]
    separator_index = number_extract.find('^')
    first_block = number_extract[separator_index+1:]
    second_block = number_extract[:separator_index]
    formed_length = len(first_block) + len(second_block)
    
    if formed_length < 30:
        to_fill = formed_length - 30
        zeroes =''
        for i in range(0, to_fill):
            zeroes += '0'
        if len(second_block) < 0:
            zeroes = '-'+ zeroes
        second_block = zeroes + second_block
        
    return first_block + second_block

def get_blackhawk_upc_code(cnumber):
    upc_code = cnumber[:11]
    return upc_code

def get_woolworth_upc_code(cnumber):
    # First 9 digits of a card is a batch number. 
    # +6280003090916632185=271050212593?
    upc_code = cnumber[:9]

    return upc_code


def extract_card_number(card_number, card_type):
    if card_number != None and card_type != None:
        if card_type in CARD_TYPES[0]:
            return woolworth_card_number(card_number)
        if card_type in CARD_TYPES[1]:
            return blackhawk_card_number(card_number)  
    else:
        return card_number

def extract_cnumber(cnumber):
    check = len(cnumber)
    
    if check == 19:
        upc_code = cnumber[:9]
        return upc_code
    if check == 30:
        upc_code = cnumber[:11]
        return upc_code
    clean= cnumber[:2]
    spcl = cnumber.find("=")
    if spcl != -1:
       if (clean == "%B"):
           cleaned =  blackhawk_card_number(cnumber)
           upc_code = get_blackhawk_upc_code(cleaned)  
           return upc_code
           
       else:
           cleaned =  woolworth_cnumber(cnumber)
           upc_code = get_woolworth_upc_code(cleaned)
           return upc_code
           
def woolworth_cnumber(cnumber):
  number = cnumber[1:cnumber.find('=')]
  print "Here"	
  print 'processed %s' % number 
  return number

def woolworth_cnumber_manual(cnumber):
  return cnumber;

def blackhawk_card_number(cnumber):
    number_extract = cnumber[2:cnumber.find(' ')]
    separator_index = number_extract.find('^')
    first_block = number_extract[separator_index+1:]
    second_block = number_extract[:separator_index]
    formed_length = len(first_block) + len(second_block)
    
    if formed_length < 30:
        to_fill = formed_length - 30
        zeroes =''
        for i in range(0, to_fill):
            zeroes += '0'
        if len(second_block) < 0:
            zeroes = '-'+ zeroes
        second_block = zeroes + second_block
        
    return first_block + second_block

def verify_card_length(card_type, card_number):
    if 'E' in card_number:
        return False
    if card_type:
        length = len(card_number)
        if card_type in CARD_TYPES[0] and length == 19:
            return True
        elif card_type in CARD_TYPES[1] and length == 30:
            return True
        else:
            return False

def get_cards_for_batch(batch_number):
    result = bulk_cards.objects.filter(batch=generated_batch.objects.get(batch_number=batch_number))
    return result
#
def get_batch_for_user(email):
    result = generated_batch.objects.filter(assigned_to=email,active_status=False)
    return result
#
def update_card_details(request):
    batch_number = 0
    batch_id=0
    saved_card = None
    for k, v in request.POST.items():
        if k.startswith('c_'):
            if v:
                try:
                    card_pk = int(k[2:])            
                    saved_card = bulk_cards.objects.get(id=card_pk)            
                    saved_card.cost = v
                    saved_card.save()
                except:
                    pass
            
    batch_id = saved_card.batch_id
    batch = generated_batch.objects.get(pk=batch_id)
    update_batch_total(batch)
    #print batch_id, batch.batch_number
    request.session['batch_number'] = batch.batch_number
    
def update_batch_total(batch=None):
    if batch != None:
        total = 0
        cards = bulk_cards.objects.filter(batch_id = batch)
        for card in cards:
            total += card.cost
        batch.total_cost=total
        batch.save()
#        
def create_new_batch(number_of_cards,cost_per_card,new_batch_num,card_type,created_by_user):
    
     # create a generated batch
        new_batch = generated_batch(
                                batch_number=new_batch_num,
                                created_by=created_by_user,
                                card_type=card_type, total_cost=0, assigned_to=created_by_user)
        create_cards = False
        cards_created = 0
        try:
            new_batch.save()
            create_cards = True
        except:
            pass
            
        # create new cards for the batch
        if create_cards:
            total = 0
            
            for card in range(0, number_of_cards):
                print 'card %d cost %d' % (new_batch_num, cost_per_card)
                total += cost_per_card
                try:
                    new_card = bulk_cards(card_number=new_batch_num, cost=cost_per_card, batch=new_batch)
                    new_card.save()
                    new_batch_num += 1
                    cards_created += 1
                except:
                    pass
            new_batch.total_cost = total
            new_batch.save()
            
        return cards_created
    
def get_next_batch_number(batch_number):
    # log this for debugging
    new_batch = str(int(batch_number) + 10000).zfill(len(batch_number))
    return new_batch
