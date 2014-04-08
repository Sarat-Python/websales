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
  0.9    339      NaveeN      08/04/2014  Base file for BlackHawk card activation
 End Change Log ***************************************************************
'''

import argparse
import urllib2
from xml.etree import ElementTree as etree
from xml.dom.minidom import Document

from log import Logger
def get_request_type(request_api):
    request_type = ''
    if request_api == "activate":
        request_type = "ActivateRequest"
    elif request_api == "void":
        request_type = "VoidRequest"
    elif request_api == "reload":
        request_type = "ReloadRequest"
    elif request_api == "pin":
        request_type = "PinOnReceiptRequest"
    elif request_api == "voidpin":
        request_type = "VoidPinOnRequest"
    elif request_api == "balance":
        request_type = "BalanceRequest"
    elif request_api == "redeem":
        request_type = "RedeemRequest"
    return request_type


def generate_xml_request(requested_item,requested_amount,transaction_id,request_api="activate"):
    '''
    Generates XML request for the gift card
    requested_item = Item's 30 digits Unique Product Code (UPC). Eg:076750047367979790000023212407
    requested_amount = amount of the product. send 3000 for $30 as a parameter.
    transaction_id = ID of the transaction that is to be done
    request_api = Send any one of the strings from below mentioned list
    -------------------------------------------------------------------
    1. activate - Default. No need to send anything in the parameter.
    2. void
    3. reload
    4. pin
    5. voidpin
    6. balance
    7. redeem
    -------------------------------------------------------------------
    '''
    is_reversal = "true" if request_api == "void" else "false" 
    
    REQUEST_URL = 'http://activate.test.conn3cted.com/api/'
    #API_KEY = 'e4e37d00-efc0-4f16-977c-8bb14f733386'
    API_KEY = 'e4e37d00DefcoT4f16V977cr8bb14f7333'
    TERMINAL_ID = '999'
    STORE_ID = '99999'        
    
    doc = Document()
    request_str = ""
    
    Logger.get_logger(__name__).info("          START OF THE NEW GIFT CARD TRANSACTION          ")
    Logger.get_logger(__name__).info("**********************************************************")
    Logger.get_logger(__name__).info("PRODUCT UPC CODE           : " + str(requested_item))
    Logger.get_logger(__name__).info("TRANSACTION ID             : " + str(transaction_id))
    Logger.get_logger(__name__).info("TRANSACTION TYPE           : " + request_api)
    Logger.get_logger(__name__).info("(TRANSACTION AMOUNT * 100) : " + str(requested_amount*100))
    Logger.get_logger(__name__).info("**********************************************************")
    try:
        request_element = get_request_type(request_api)
    
        if request_element != '': 
            entity_descriptor = doc.createElement(request_element)
            doc.appendChild(entity_descriptor)
            entity_descriptor.setAttribute('xmlns', 'http://www.conn3cted.com/schemas/2012')
            entity_descriptor.setAttribute('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
            entity_descriptor.setAttribute('xsi:schemaLocation', 'http://www.conn3cted.com/schemas/2012/Conn3cted_Cards_1.0.xsd')
            
            req_header = doc.createElement('ReqHeader')
            entity_descriptor.appendChild(req_header)
            
            api_tag = doc.createElement('APIKey')
            api_key = doc.createTextNode(API_KEY)
            api_tag.appendChild(api_key)
            req_header.appendChild(api_tag)
            
            txn_id_tag = doc.createElement('TransactionID')
            txn_id = doc.createTextNode(str(transaction_id))
            txn_id_tag.appendChild(txn_id)
            req_header.appendChild(txn_id_tag)
            
            txn_reverse_tag = doc.createElement('IsReversal')
            is_reverse = doc.createTextNode(is_reversal)
            txn_reverse_tag.appendChild(is_reverse)
            req_header.appendChild(txn_reverse_tag)
        
            req_body = doc.createElement('ReqBody')
            entity_descriptor.appendChild(req_body)
        
            terminal_id_tag = doc.createElement('TerminalID')
            terminal_id = doc.createTextNode(TERMINAL_ID)
            terminal_id_tag.appendChild(terminal_id)
            req_body.appendChild(terminal_id_tag)
        
            store_id_tag = doc.createElement('StoreID')
            store_id = doc.createTextNode(STORE_ID)
            store_id_tag.appendChild(store_id)
            req_body.appendChild(store_id_tag)
        
            product_id_tag = doc.createElement('Number')
            product_code = doc.createTextNode(str(requested_item))
            product_id_tag.appendChild(product_code)
            req_body.appendChild(product_id_tag)
        
            amount_tag = doc.createElement('Amount')
            txn_amount = doc.createTextNode(str(int(requested_amount)))
            amount_tag.appendChild(txn_amount)
            req_body.appendChild(amount_tag)
            
            root = etree.fromstring(doc.toxml())
            #Logger.get_logger(__name__).info("Requesting: " + etree.tostring(root))
            xml_request = urllib2.Request(url = (REQUEST_URL + request_api), data = etree.tostring(root))
        
            response = urllib2.urlopen(xml_request)
            xml_response = response.read()
            Logger.get_logger(__name__).info("Response: " + xml_response)
            xml_element = etree.XML(xml_response)
            return {'xml_response':xml_response}
    except Exception as e:
        Logger.get_logger(__name__).error("Error while requesting gift card " + str(e))
        return {'status':'ERROR','request':request_str,'response':str(e)}

