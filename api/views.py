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

Begin Change Log ***********************************************************
  Itr         Def/Req    Userid      Date           Description
  -----     --------    --------   --------     -----------------------------
  Sprint3   Story #38   NaveeN      11/04/2014  Implemented Items in shopping
												cart not getting cleared
 End Change Log ************************************************************

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

error_codes = {
                '0': 'OK',
                '101':'Invalid BalanceId',
                '102':'Balance is not active',
                '103':'Balance valid from date is in the future',
                '104':'Balance valid to date (including grace period) is in the past',
                '109':'insufficient balance',
                '111':'Balance Not Available For Issue',
                '113': 'The amount you have entered is above your maximum limit of $#',
                '122': 'Invalid amount for this transaction',
                '134': 'DeliveryDate cannot be in the past',
                '135' : 'Invalid VoucherProductCode',
                '200' : 'Invalid CredentialCode',
                '201' : 'Invalid CredentialCode',
                '201' : 'Invalid CredentialCode or Card Pin Number',
                '204' : 'Invalid CredentialCode or ExpiryDate YYYY-MM',
                '204' : 'Invalid CredentialCode or VoucherExpiryDate',
                '204' : 'Invalid CredentialCode or Access Password',
                '204' : 'Invalid CredentialCode or Expiry MM/YY',
                '205' : 'Credential is not active',
                '250' : 'Invalid Username and Password',
                '254' : 'Invalid CredentialCode or CredentialPassword',
                '301' : 'Invalid MerchantOutletCode',
                '305' : 'Store [#] not in voucher program [#]',
                '305' : 'Store [#] not in voucher program [#] As a Redemption Store',
                '310' : 'Store [#] does not have an account',
                '401' : 'Invalid Retailer',
                '402' : 'Inactive Redeeming Retailer [#]',
                '403' : 'Inactive Voucher Program [#]',
                '504' : 'Original request message is not of a type that supports undo',
                '507' : 'Transaction previously cancelled by RequestMessageId #########',
                '508' : 'Can''t undo activation - voucher has been redeemed',
                '606' : 'No-Settlement Store do not allow Transaction with other Settlement Stream',
                '806' : 'You do not have access to this function.',
                '806' : 'You do not have access to this Voucher Product',
                '990' : 'Store [#] not in voucher program [#]',
                '2001' : 'Error in XML Document (line, character)',
                '2001' : 'SVML Timeout',
                '9999':'NOT_AUTHORIZED'
                }



class obj(object):
	def __init__(self, d):
		for a, b in d.items():
			if isinstance(b, (list, tuple)):
				setattr(self, a, [obj(x) if isinstance(x, dict) else x for x in b])
			else:
				setattr(self, a, obj(b) if isinstance(b, dict) else b)


def process_cart(request,direct_checkout=''):

	'''
	direct_checkout : @param to check if user comes from swiped card details list page
	activated : success : 0, failure:1
	ret_status: success : 0, failure:1, partial:2

	'''
	if direct_checkout:
		card_items = SwipedCard.objects.filter(cart_status=0)
		for flag in card_items:
			flag.cart_status = 1
			flag.save()
	process_items = SwipedCard.objects.values('card_number','amount',
			'card_type','gift_card_id','card_flavour').filter(cart_status__in=[1])
	#print process_items.query()
	Logger.initialize('wex.log', True, 'LOG_DEBUG')
	response_dict = {}
	txn_status = []
	partial = []
	d = {}
	credential_codes = []
	credential_codes_amount = []
	for item in process_items:
		if item['card_type'] == 'WLWRTH':
			#credential_codes = []
			#credential_codes_amount = []
			response_from = {}
			credential_codes.insert(0, item['card_number'])
			credential_codes_amount.insert(0, item['amount'])
	 		txn_id = 0
			try:
				f = open('request_message_id.txt', 'r')
				lines = f.readlines()
				txn_id = int(lines[0][13:])
				f.close()
			except Exception as e:  
				print "Transaction ID will reset to 1"
			f = open('request_message_id.txt', 'w')
			new_txn_id = 'wex-test-ind-' + str(txn_id + 1)
			f.write(new_txn_id)
			f.close()
			xml_response = activation_request(credential_codes
					, credential_codes_amount, new_txn_id)
			dom = parseString(xml_response['xml_response'])
			ResultCode = dom.getElementsByTagName('ResultCode')[1].firstChild.nodeValue
			Description = dom.getElementsByTagName('Description')[1].firstChild.nodeValue
			card_number = item['card_number']
			if ResultCode == 0:
				activation_status = 'success'
				activated = 0
			else:
				activation_status = 'failure'
				activated = 1
			response_from = {'ResultCode':error_codes[ResultCode],'Description':Description,
							'card_number':card_number,
							'activation_status':activation_status,
							'card_flavour': item['card_flavour']}
			txn_status.append(ResultCode)
			response_dict[card_number] = obj(response_from)
			cart_status_details = SwipedCard.objects.filter(cart_status=1)
			for flag_activated in cart_status_details:
				flag_activated.cart_status = 2
				flag_activated.activated = activated
				flag_activated.save()
        	#web_txns = web_txn_gift_cards(gift_card_price = item['amount'],
			#card_type = item['card_type'],gift_card_id = 0,
			#activate_success=0,void_request=0,void_success=0,status='1',
			#txn_id=123,remarks='remarks',activate_request = xml_response['request_data'],
			#	activate_response = xml_response['xml_response']
			#)
			#web_txns.save()
		elif item['card_type'] == 'BLKHWK':
	 		txn_id = 0
			try:
				f = open('request_message_id.txt', 'r')
				lines = f.readlines()

				txn_id = int(lines[0][13:])
				f.close()
			except Exception as e:  
				#print str(e)
				print "Transaction ID will reset to 1"

			f = open('request_message_id.txt', 'w')
			new_txn_id = 'wex-test-ind-' + str(txn_id + 1)
			f.write(new_txn_id)
			f.close()
			request_status = generate_xml_request(item['card_number'],
								item['amount'],new_txn_id)
			dom = parseString(request_status['xml_response'])
			Status = dom.getElementsByTagName('Status')[0].firstChild.nodeValue
			card_number = item['card_number']
                        
     			if Status == 'NOT_AUTHORIZED':
				activation_status = 'failure'
			        ResultCode = '9999'
				activated = 1
			else:
				activation_status = 'success'
                                ResultCode = '0'
				activated = 0
			response_from = {'ResultCode':error_codes[ResultCode],
							'Description':Status,
							'card_number':card_number,
							'activation_status':activation_status,
						'card_flavour': item['card_flavour']}
			response_dict[card_number] = obj(response_from)
			txn_status.append(ResultCode)

			cart_status_details = SwipedCard.objects.filter(cart_status=1)
			for flag_activated in cart_status_details:
				flag_activated.cart_status = 2
				flag_activated.activated = activated
				flag_activated.save()

			#web_txns = web_txn_gift_cards(gift_card_price = item['amount'],
			#card_type = item['card_type'],gift_card_id = 0,
			#	activate_success=0,void_request=0,void_success=0,status='1',
			#txn_id=123,remarks='remarks',activate_request = xml_response['request_data'],
			#	activate_response = xml_response['xml_response']
			#)
			#web_txns.save()


#		d = { x:txn_status.count(x) for x in txn_status }

		for x in txn_status:
			d[x]= txn_status.count(x)

		for key, value in d.iteritems():
			partial.append(int(key))

		partial.sort()
		if partial.count(0) == 0:
			ret_status = 1
		elif partial.count(0) == len(partial):
			ret_status = 0
		else:
			ret_status = 2
		
		request.session['cartcount'] = ''
	return render(request,'process.html', {'response_details':response_dict,
				 'txn_status':ret_status,'txn_id':txn_id})

