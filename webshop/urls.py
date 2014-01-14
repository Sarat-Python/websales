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
        url(r'^termsandconditions/$', 'webshop.views.terms'),
	
	# user registration and authentication module
	url(r'^user/', include('users.urls')),
        
        # card management app
        url(r'^cards/', include('cards.urls')),
        
        # shopping module
        url(r'^shopping/', include('shopping.urls')),
)
