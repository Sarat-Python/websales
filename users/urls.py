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
