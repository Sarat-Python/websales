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
  0.9    339      NaveeN      08/04/2014  Added model to store Activation Response
 End Change Log ***************************************************************
'''


from django.db import models

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
