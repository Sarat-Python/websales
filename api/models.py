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
  0.9    339      NaveeN      30/04/2014  Added model to Payment Response
 End Change Log ***************************************************************
'''


from django.db import models

class WebsalesTxnHeads(models.Model):
    id = models.IntegerField(primary_key=True)
    websales_site_id = models.IntegerField()
    websales_txn_id = models.IntegerField()
    txn_type = models.CharField(max_length=10)  # Recharge: R, GiftCard: G, Epay: P, Surcharge: S
    payment_mode = models.CharField(max_length=150)
    customer_image = models.CharField(max_length=150)
    txn_amount = models.FloatField(max_length=150)
    collected_amount = models.FloatField()
    customer_id = models.IntegerField()
    payment_status = models.CharField(max_length=150)
    txn_date = models.DateTimeField(auto_now_add=True)
    receipt_status = models.IntegerField()
    payment_receipt = models.CharField(max_length=150)
    refund_status = models.IntegerField()
    txn_refunded = models.IntegerField()
    txn_cancelled = models.IntegerField()
    txn_other = models.IntegerField()
    last_updated_on = models.DateTimeField()
    last_updated_by = models.IntegerField()
    payment_card_type = models.CharField(max_length=150)
    payment_card_number = models.IntegerField()
    payment_account_type = models.CharField(max_length=150)
    payment_response = models.CharField(max_length=150)
    class Meta:
       db_table = 'websales_txn_heads'


class WebsalesTxnDetails(models.Model):
    id = models.IntegerField(primary_key=True)
    txn_head_id = models.IntegerField()
    gift_card_id = models.IntegerField()
    gift_card_txn_id = models.CharField(max_length=50)
    gift_card_code = models.CharField(max_length=30)
    gift_card_price = models.FloatField()
    activate_request = models.TextField()
    activate_response = models.TextField()
    activate_success = models.IntegerField()
    void_request = models.TextField()
    void_response = models.TextField()
    void_success = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField()
    expiry_date = models.DateField()
    gift_card_receipt = models.CharField(max_length=30)
    profit_percentage = models.FloatField()
    profit_amount = models.FloatField()
    gst_in_commission = models.FloatField()
    comm_overpayment = models.FloatField()
    gst_overpayment = models.FloatField()
    errorcode = models.CharField(max_length=30)
    service_charge = models.FloatField()

    class Meta:
       db_table = 'websales_txn_details'

# Create your models here.
class web_txn_gift_cards(models.Model):
    id = models.IntegerField(primary_key=True)
    txn_id = models.CharField(max_length=10)
    gift_card_id = models.IntegerField(max_length=10)
    gift_card_txn_id = models.CharField(max_length=150)
    gift_card_code =models.CharField(max_length=50)
    gift_card_price = models.FloatField()
    activate_request = models.TextField()
    activate_response = models.TextField()
    void_request = models.CharField(max_length=150)
    void_response = models.IntegerField(max_length=4)
    activate_success = models.IntegerField(max_length=4)
    void_request = models.IntegerField(max_length=4)
    void_success = models.IntegerField(max_length=4)
    card_type = models.CharField(max_length=10)
    status = models.IntegerField(max_length=4)
    remarks = models.CharField(max_length=4)		
    class Meta:
       db_table = 'web_txn_gift_cards'

class websales_sites(models.Model):
    id = models.IntegerField(primary_key=True)
    identifier = models.CharField(max_length=14)	
    
    class Meta:
       db_table = 'websales_sites'
