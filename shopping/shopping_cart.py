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
Begin Change Log ***************************************************************
                                                                      
  Itr    Def/Req  Userid      Date       Description
  -----  -------- --------    --------   --------------------------------------
  0.9    339      prashanth  19/01/2014  Added copyright Info
 End Change Log ****************************************************************
'''

import datetime
import models

# This is an extension of the django-cart reference impl
#
#CART_ID = 'CART-ID'
#
#class ItemAlreadyExists(Exception):
#    pass
#
#class ItemDoesNotExist(Exception):
#    pass
#
#class Cart:
#    def __init__(self, request):
#        cart_id = request.session.get(CART_ID)
#        if cart_id:
#            try:
#                cart = models.Cart.objects.get(id=cart_id, checked_out=False)
#            except models.Cart.DoesNotExist:
#                cart = self.new(request)
#        else:
#            cart = self.new(request)
#        self.cart = cart
#
#    def __iter__(self):
#        for item in self.cart.item_set.all():
#            yield item
#
#    def create_cart(self, request):
#        cart = models.Cart(creation_date=datetime.datetime.now())
#        cart.save()
#        request.session[CART_ID] = cart.id
#        return cart
#
#    def add_product(self, product, unit_price, quantity=1):
#        try:
#            item = models.Item.objects.get(
#                cart=self.cart,
#                product=product,
#            )
#        except models.Item.DoesNotExist:
#            item = models.Item()
#            item.cart = self.cart
#            item.product = product
#            item.unit_price = unit_price
#            item.quantity = quantity
#            item.save()
#        else:
#            raise ItemAlreadyExists
#
#    def remove_product(self, product):
#        try:
#            item = models.Item.objects.get(
#                cart=self.cart,
#                product=product,
#            )
#        except models.Item.DoesNotExist:
#            raise ItemDoesNotExist
#        else:
#            item.delete()
#
#    def update_cart(self, product, quantity, unit_price=None):
#        try:
#            item = models.Item.objects.get(
#                cart=self.cart,
#                product=product,
#            )
#        except models.Item.DoesNotExist:
#            raise ItemDoesNotExist
#
#    def clear_cart(self):
#        for item in self.cart.item_set:
#            item.delete()

