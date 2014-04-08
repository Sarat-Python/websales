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
  0.9    339      NaveeN      08/04/2014  Base file for Woolworths card activation
 End Change Log ***************************************************************
'''

import argparse
import datetime
import urllib2
from xml.etree import ElementTree as etree
from xml.dom.minidom import Document

from log import Logger

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
                '2001' : 'SVML Timeout'
                }


def create_sign_on_request(uname='Pitstop_kiosk_QA', password='Temp1234'):
    sign_on_request = '<SignonRequest>'
    sign_on_request += '<UserName>' + uname + '</UserName>'
    sign_on_request += '<Password>' + password + '</Password>'
    sign_on_request += '</SignonRequest>'
    return sign_on_request


def activation_request(credential_codes, credential_codes_amount, request_message_id):
   
    try:
        REQUEST_URL = 'https://svml.qa.ecomindustries.com.au/svml/default.aspx'
        MERCHANT_OUTLET_CODE = '8129'
        request_data = '<?xml version="1.0" encoding="utf-8"?>'
        request_data += '<SVML xmlns="http://ecomindustries.com.au/SVML/">'
        request_data += '<ActivationRequestMessage>'
        request_data += '<RequestMessageId>' + request_message_id + '</RequestMessageId>'
        request_data += create_sign_on_request()
        request_data += '<ActivationRequests>'
        for idx, code in enumerate(credential_codes):
            request_data += '<ActivationRequest>'
            request_data += '<CredentialCode>' + code + '</CredentialCode>'
            request_data += '<MerchantOutletCode>' + MERCHANT_OUTLET_CODE + '</MerchantOutletCode>'
            request_data += '<Amount>' + str(credential_codes_amount[idx]) + '</Amount>'
            request_data += '<Reference>' + request_message_id + '-' + str(idx) + '</Reference>'
            request_data += '</ActivationRequest>'
        request_data += '</ActivationRequests>'
        request_data += '</ActivationRequestMessage>'
        request_data += '</SVML>'

        Logger.get_logger(__name__).info("***********************************")
        Logger.get_logger(__name__).info("       ACTIVATION RESQUEST         ")
        Logger.get_logger(__name__).info("***********************************")
        Logger.get_logger(__name__).info(request_data)
        Logger.get_logger(__name__).info("***********************************")
	
        xml_request = urllib2.Request(url=(REQUEST_URL), data=request_data)

        response = urllib2.urlopen(xml_request)
        xml_response = response.read()
        Logger.get_logger(__name__).info("       ACTIVATION RESPONSE         ")
        Logger.get_logger(__name__).info("***********************************")
        Logger.get_logger(__name__).info(xml_response)
        Logger.get_logger(__name__).info("***********************************")
        #return xml_response
        return {'xml_response':xml_response,'request_data':request_data} 
    except Exception as e:
        Logger.get_logger(__name__).error("Error while requesting WEX gift card " + str(e))
        return {'status':'ERROR', 'request':xml_request, 'response':str(e)}


def send_request_to_wex(txn_type, credential_codes, credential_codes_amount, request_message_id):
    if txn_type == 'A':
        activation_request(credential_codes, credential_codes_amount, request_message_id)
    return "INVALID"

