#from cards.models import generated_batch, bulk_cards
from card_info import CARD_TYPES

#def clean_save_card():

def extract_upc_code(card_number, card_type):
     if card_number != None and card_type != None:
        if card_type in CARD_TYPES[0]:
            return get_woolworth_upc_code(card_number)
        if card_type in CARD_TYPES[1]:
            return get_blackhawk_upc_code(card_number)
        else:
            return None

def get_blackhawk_upc_code(card_number):
    # First 11 digits of a card is a upc code.
    upc_code = card_number[:11]
    return upc_code


def get_woolworth_upc_code(card_number):
    # First 9 digits of a card is a batch number. +6280003090916632185=271050212593?
    upc_code = card_number[:9]
    return upc_code

def extract_card_number(card_number, card_type):
    if card_number != None and card_type != None:
        if card_type in CARD_TYPES[0]:
            return woolworth_card_number(card_number)
        if card_type in CARD_TYPES[1]:
            return blackhawk_card_number(card_number)
    else:
        return card_number

def woolworth_card_number(swipe_data):
  #// Woolworth Gift Card
  #// 19 char. long
  #// swipe_data = ';6280005000012354202=271150216491?'
  #// card_number = 6280005000012354202  
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
#def get_cards_for_batch(batch_number):
#    result = bulk_cards.objects.filter(batch=generated_batch.objects.get(batch_number=batch_number))
#    return result
#
#def get_batch_for_user(email):
#    result = generated_batch.objects.filter(assigned_to=email,active_status=False)
#    return result
#
#def update_card_details(request):
#    batch_number = 0
#    batch_id=0
#    saved_card = None
#    for k, v in request.POST.items():
#        if k.startswith('c_'):
#            if v:
#                try:
#                    card_pk = int(k[2:])            
#                    saved_card = bulk_cards.objects.get(id=card_pk)            
#                    saved_card.cost = v
#                    saved_card.save()
#                except:
#                    pass
#            
#    batch_id = saved_card.batch_id
#    batch = generated_batch.objects.get(pk=batch_id)
#    update_batch_total(batch)
#    #print batch_id, batch.batch_number
#    request.session['batch_number'] = batch.batch_number
#    
#def update_batch_total(batch=None):
#    if batch != None:
#        total = 0
#        cards = bulk_cards.objects.filter(batch_id = batch)
#        for card in cards:
#            total += card.cost
#        batch.total_cost=total
#        batch.save()
#        
#def create_new_batch(number_of_cards,cost_per_card,new_batch_num,card_type,created_by_user):
#    
#     # create a generated batch
#        new_batch = generated_batch(
#                                batch_number=new_batch_num,
#                                created_by=created_by_user,
#                                card_type=card_type, total_cost=0, assigned_to=created_by_user)
#        create_cards = False
#        cards_created = 0
#        try:
#            new_batch.save()
#            create_cards = True
#        except:
#            pass
#            
#        # create new cards for the batch
#        if create_cards:
#            total = 0
#            
#            for card in range(0, number_of_cards):
#                print 'card %d cost %d' % (new_batch_num, cost_per_card)
#                total += cost_per_card
#                try:
#                    new_card = bulk_cards(card_number=new_batch_num, cost=cost_per_card, batch=new_batch)
#                    new_card.save()
#                    new_batch_num += 1
#                    cards_created += 1
#                except:
#                    pass
#            new_batch.total_cost = total
#            new_batch.save()
#            
#        return cards_created
#    
#def get_next_batch_number(batch_number):
#    # log this for debugging
#    new_batch = str(int(batch_number) + 10000).zfill(len(batch_number))
#    return new_batch
