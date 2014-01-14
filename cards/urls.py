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
