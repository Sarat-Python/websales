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
    
    url(r'^$', 'users.views.login'),
    
    # For user registration
    url(r'^register/$', 'users.views.register'),
    # For activation
    url(r'^register/activate/$', 'users.views.activate'),
    url(r'^register/response/$', 'users.views.register_response'),
    
    # For logging in
    url(r'^login/$', 'users.views.login'),
    url(r'^logout', 'users.views.logout'),
    url(r'^loggedin/$', 'users.views.loggedin'),
    url(r'^invalid/$', 'users.views.invalid'),
    
    #For updates
    url(r'^change/password/$', 'users.views.change_password'),
    #url(r'^change/details/$', 'users.views.change_details'),
)
