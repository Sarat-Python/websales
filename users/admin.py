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

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from users.models import WebUser
from users.forms import WebUserChangeForm, WebUserCreationForm

class WebUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = WebUserChangeForm
    add_form = WebUserCreationForm

    # The fields to be used in displaying the User model.
    list_display = ('email', 'first_name', 'last_name', 'mobile', 'is_active')
    #list_filter = ('is_admin',)
    
    # These override the definitions on the base UserAdmin
    # that reference the removed 'username' field (_('Contact info'), {'fields':('email', 'mobile')}),
        #(_('Security'), {'fields':('password')}),
        #(_('Miscellaneous'), {'fields':('mobile_model','interest')}),
        #(_('Address'), {'fields':('unit', 'street', 'suburb','post code')}),
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'middle_name', 'last_name', 'mobile')}),        
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),(_('Personal info'), {'fields': ('first_name', 'middle_name', 'last_name', 'mobile')}),        
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )
    
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

admin.site.register(WebUser, WebUserAdmin)
