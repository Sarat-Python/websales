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
                                                                      
 Itr    Def/Req  Userid    Date        Description
 -----  -------- --------  --------    -----------------------------------
 0.9    339      NaveeN    08/04/2014  Added activation card urls 
 End Change Log ************************************************************
'''

from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # For bulk card activation
    url(r'^process_cart/$', 'api.views.process_cart'),
)


