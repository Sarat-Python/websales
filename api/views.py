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
                                                                      
  Itr    Def/Req  Userid      Date          Description
  -----  -------- --------    --------    --------------------------------------
  0.9    339      NaveeN      08/04/2014  Added functionality for Card Activation
 End Change Log ***************************************************************
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
from django.contrib.auth.decorators import login_required
from cards.forms import SwipedCardForm, UpdateSwipedCardForm, UpdateFormSet
from cards.models import SwipedCard, Batch, shopcart,gift_cards,EnumField
from api.models import web_txn_gift_cards
from django_tables2 import RequestConfig
from users.models import WebUser
from django.db.models import Count,Sum
from django.core import serializers
from django.utils import simplejson
from cards.card_utils import verify_card_length
from pprint import pprint
import os
from log import Logger

import wexapi
from wexapi import send_request_to_wex,activation_request
import blackhawkapi
from blackhawkapi import generate_xml_request
from xml.dom.minidom import parseString

def process_cart(request):
	process_items = SwipedCard.objects.values('card_number','amount',
			'card_type','gift_card_id').filter(cart_status__in=[1])
	Logger.initialize('wex.log', True, 'LOG_DEBUG')
	response_dict = {}
	for item in process_items:
		if item['card_type'] == 'WLWRTH':
			credential_codes = []
			credential_codes_amount = []
			response_from = {}
			credential_codes.insert(0, item['card_number'])
			credential_codes_amount.insert(0, item['amount'])
	 		txn_id = 0
			try:
				f = open('request_message_id.txt', 'r')
				lines = f.readlines()
				txn_id = int(lines[0][9:])
				f.close()
			except Exception as e:  
				print "Transaction ID will reset to 1"
			f = open('request_message_id.txt', 'w')
			new_txn_id = 'wex-test-' + str(txn_id + 1)
			f.write(new_txn_id)
			f.close()
			xml_response = activation_request(credential_codes
					, credential_codes_amount, new_txn_id)
			dom = parseString(xml_response['xml_response'])
			ResultCode = dom.getElementsByTagName('ResultCode')[1].firstChild.nodeValue
			Description = dom.getElementsByTagName('Description')[1].firstChild.nodeValue
			card_number = item['card_number']
			response_from = {'ResultCode':ResultCode,'Description':Description,'card_number':card_number}
			response_dict[card_number] = response_from
        		#web_txns = web_txn_gift_cards(gift_card_price = item['amount'],card_type = item['card_type'],gift_card_id = 0,activate_success=0,void_request=0,void_success=0,status='1',txn_id=123,remarks='remarks',activate_request = xml_response['request_data'],
			#	activate_response = xml_response['xml_response']
			#)
			#web_txns.save()
		elif item['card_type'] == 'BLKHWK':
	 		txn_id = 0
			try:
				f = open('request_message_id.txt', 'r')
				lines = f.readlines()
				txn_id = int(lines[0][9:])
				f.close()
			except Exception as e:  
				#print str(e)
				print "Transaction ID will reset to 1"

			f = open('request_message_id.txt', 'w')
			new_txn_id = 'conn-test-' + str(txn_id + 1)
			f.write(new_txn_id)
			f.close()
			request_status = generate_xml_request(item['card_number'],item['amount'],new_txn_id)
			dom = parseString(request_status['xml_response'])
			Status = dom.getElementsByTagName('Status')[0].firstChild.nodeValue
			card_number = item['card_number']
			response_from = {'ResultCode':'','Description':Status,
							'card_number':card_number}
			response_dict[card_number] = response_from

			#web_txns = web_txn_gift_cards(gift_card_price = item['amount'],card_type = item['card_type'],gift_card_id = 0,activate_success=0,void_request=0,void_success=0,status='1',txn_id=123,remarks='remarks',activate_request = xml_response['request_data'],
			#	activate_response = xml_response['xml_response']
			#)
			#web_txns.save()
	return render(request,'process.html', {'response_details':response_dict})
