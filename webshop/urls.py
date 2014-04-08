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
                                                                      
  Itr    Def/Req  Userid      Date       Description
  -----  -------- --------    --------   --------------------------------------
  0.9    339      NaveeN  08/04/2014  Added api url path
 End Change Log ***************************************************************
'''

from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

from django.views.generic import TemplateView

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webshop.views.home', name='home'),
    # url(r'^webshop/', include('webshop.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
	url(r'^admin/', include(admin.site.urls)),
	
	# webshop home
	url(r'^$', TemplateView.as_view(template_name='index.html')),
        url(r'^home/$', TemplateView.as_view(template_name='index.html')),
        url(r'^about/$', TemplateView.as_view(template_name='about.html')),
        url(r'^contact/$', TemplateView.as_view(template_name='contact.html')),
        #url(r'^home/$', 'webshop.views.home'),
        #url(r'^about/$', 'webshop.views.about'),
        #url(r'^contact/$', 'webshop.views.contact'),
        url(r'^termsandconditions/$', 'webshop.views.terms'),
	
	# user registration and authentication module
	url(r'^user/', include('users.urls')),
        
        # card management app
        url(r'^cards/', include('cards.urls')),
        
        # shopping module
        url(r'^shopping/', include('shopping.urls')),

        # shopping module
        url(r'^api/', include('api.urls')),

)
