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
                                                                      
 Itr      Def/Req     Userid    Date        Description
 -----   --------   --------   --------    ---------------------------------
 Sprint3  Story#21    Sarat    04/04/2014  Added goto_cart param 
 End Change Log ************************************************************
'''

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
   
    # For bulk card activation
    url(r'^bulk/load_flavours/$', 'cards.views.load_flavours'),
    url(r'^bulk/purchase/$', 'cards.views.bulk'),
    url(r'^bulk/update/$', 'cards.views.update'),
    url(r'^bulk/add_cart/$', 'cards.views.add_cart', name="add_cart"),
    url(r'^shop/shop_cart/$', 'cards.views.add_cart', name="add_cart"),
    url(r'^shop/goto_cart/$', 'cards.views.goto_cart', name="goto_cart"),
    url(r'^bulk/del_cart/$', 'cards.views.del_cart'),
    url(r'^bulk/(?P<cart>\w+)/$', 'cards.views.bulk'),
    url(r'^bulk/(?P<cart>\w+)/(?P<from_cart>\w+)/$', 'cards.views.bulk'),
    #url(r'^bulk/(?P<cart>\w+)/(?P<from_cart>\w+)/(?P<changes>\w+)/$', 'cards.views.bulk'),   
)


