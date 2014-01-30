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

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webshop.views.home', name='home'),
    # url(r'^webshop/', include('webshop.foo.urls')),
    
    #url(r'^$', 'users.views.login'),
    
    # For bulk card activation
    url(r'^bulk/purchase/$', 'cards.views.bulk'),
    url(r'^bulk/update/$', 'cards.views.update'),
    #url(r'^bulk/edit/$', 'cards.views.bulk_edit'),
    #url(r'^bulk/update/$', 'cards.views.bulk_update'),
    url(r'^purchase/$', 'cards.views.purchase'),
    #url(r'^activate/batch/$', 'cards.views.activate_batch'),
   
)
