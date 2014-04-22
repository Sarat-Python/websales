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
                                                                      
  Itr          Def/Req    Userid      Date       Description
  -----       --------    -------    --------   -------------------------------
  Story #44    Task #46   Sarat      22/04/2014   Added Account Settings 
                                                  functionality.
 End Change Log ***************************************************************
'''

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.forms.models import modelformset_factory
from django.db import models
from django.forms import ModelForm
from users.models import WebUser,kiosk_venues
from users.models import WebUser

def populateVenues():
	venue = []
	choices=kiosk_venues.objects.values('id','name').filter(is_deleted=0)
	for venues in choices:
		venue.append((venues['id'],venues['name']))
	return venue

choices = populateVenues()
venues = [('','         ')] + choices

# can be used at both admin and shopping sites
class WebUserCreationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """
    email = forms.EmailField(required = True)
    first_name = forms.CharField(min_length=3, max_length= 30,required = True)
    middle_name = forms.CharField(required = False)
    last_name = forms.CharField(max_length= 30,required = True)
    mobile = forms.CharField(max_length= 20,required = True)
    mobile_model = forms.CharField(required = False, widget=forms.Select(), initial="-select-")
    unit = forms.CharField(max_length= 30,required = False)
    street = forms.CharField(max_length= 10,required = False)
    suburb = forms.CharField( max_length= 10,required = False)
    postcode = forms.CharField(max_length= 30,required = False)
    interest = forms.CharField(required = False)
    terms = forms.BooleanField(required = True, initial = False)
    venue = forms.ChoiceField(choices=venues, required=False)
    
    class Meta:
        model = WebUser
        fields = ("email", "first_name",
                  "middle_name", "last_name", "mobile", "mobile_model",
                  "unit", "street", "suburb", "postcode", "interest","venue")

    UpdateSettingBase = modelformset_factory(
    WebUser, extra=0, fields=('email', 'first_name',
                  'middle_name', 'last_name', 'mobile', 'mobile_model',
                  'unit', 'street', 'suburb', 'postcode', 'interest','venue'))	
    
    def __init__(self, *args, **kargs):
        super(WebUserCreationForm, self).__init__(*args, **kargs)
        del self.fields['username']
        #del self.fields['password1'].
	self.fields['first_name'].widget.attrs = {'class':'styled form-control validate[required,custom[fname]]','maxlength':30}
        self.fields['last_name'].widget.attrs = {'class':'styled form-control validate[required,custom[fname]]','maxlength':30}
        self.fields['email'].widget.attrs = {'class':'styled form-control validate[required,custom[fname]]'}
        self.fields['password1'].widget.attrs = {'class':'styled form-control validate[required,custom[fname]]'}
        self.fields['password2'].widget.attrs = {'class':'styled form-control validate[required,custom[fname]]'}
        self.fields['mobile'].widget.attrs = {'class':'styled form-control validate[required,custom[fname]]','maxlength':20}
	self.fields['venue'].widget.attrs = {'class':'styled form-control validate[required,custom[fname]]'}
	self.fields['venue'].label = "Select Venue"
        
    def clean_email(self):
        email = self.cleaned_data['email']
        if WebUser.objects.filter(email=email).exists():
            raise ValidationError(_("Email is already registered"), code='registered')
        return email
        
# Used in admin site only
class WebUserChangeForm(UserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    #password1 = forms.CharField(widget=forms.PasswordInput(render_value=False))
    #password2 = forms.CharField(widget=forms.PasswordInput(render_value=False))
    
    def __init__(self, *args, **kargs):
        super(WebUserChangeForm, self).__init__(*args, **kargs)
        del self.fields['username']
    
    class Meta:
        model = WebUser
        #fields = ('password1', 'password2')
        
class WebPasswordChangeForm(forms.Form):
    """ A form for updating user passwords from shopping site. """
    current_password = forms.CharField(widget=forms.PasswordInput(render_value=False))
    new_password = forms.CharField(widget=forms.PasswordInput(render_value=False))
    renter_new_password = forms.CharField(widget=forms.PasswordInput(render_value=False))
     
    class Meta:
        model = WebUser
        fields = ('email',)

    
    def clean_renter_new_password(self):
        # Check that the two password entries match
        new_password = self.cleaned_data.get("new_password")
        renter_new_password = self.cleaned_data.get("renter_new_password")
        if new_password and renter_new_password and new_password != renter_new_password:
            msg = "Passwords don't match"
            raise forms.ValidationError(msg)
        return renter_new_password
    
    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(WebUserChangeForm,
                        self).save(commit=False)
        user.set_password(self.cleaned_data["new_password"])
        if commit:
            user.save()
        return user
    
    def clean_password(self, ):
        return self.initial['password']

class ActivationForm(forms.Form):
    email = forms.EmailField(required = True)
    activation_code = forms.CharField(max_length=6, required=True)
    
    def __init__(self, *args, **kwargs):            
        super(ActivationForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = u'Registered Email'
        self.fields['activation_code'].widget.attrs['placeholder'] = u'example: a0bf7f'
        self.fields['activation_code'].widget.attrs['class'] = 'styled form-control validate[required,custom[fname]]'
        self.fields['email'].widget.attrs['class'] = 'styled form-control validate[required,custom[email]]'
    
    def clean_email(self):
        email = self.cleaned_data['email']        
        return email


class WebUserSettings(forms.Form):
    """
    A form that creates a user seetings form, to alter settings.
    """
    email = forms.EmailField(required = True)
    first_name = forms.CharField(min_length=3, max_length= 30,required = True)
    middle_name = forms.CharField(required = False)
    last_name = forms.CharField(max_length= 30,required = True)
    mobile = forms.CharField(max_length= 20,required = True)
    terms = forms.BooleanField(required = True, initial = False)	
    
    class Meta:
        model = WebUser
        fields = ("email", "first_name",
                  "middle_name", "last_name", "mobile", "mobile_model",
                  "unit", "street", "suburb", "postcode", "interest","venue")

    def add_fields(self, form, index):
        super(WebUserSettings, self).add_fields(form, index)
	form.fields['first_name'] = forms.CharField(required=True)

class WebMobileChangeForm(forms.Form):
    mob = forms.CharField(max_length= 20,required = True)	
    class Meta:
        model = WebUser
        fields = ('mobile',)

	def __init__(self, *args, **kwargs):            
		    super(WebMobileChangeForm, self).__init__(*args, **kwargs)
		    self.fields['mob'].widget.attrs['class'] = 'styled form-control validate[required,custom[phone]]'
		    

    def clean_mobile(self, ):
        return self.initial['mob']	
    

class WebEmailChangeForm(forms.Form):
    eml = forms.EmailField(required = True)	
    class Meta:
        model = WebUser
        fields = ('email',)

	def __init__(self, *args, **kwargs):            
		    super(WebEmailChangeForm, self).__init__(*args, **kwargs)
		    self.fields['eml'].widget.attrs['class'] = 'styled form-control validate[required,custom[email]]'
		    

    def clean_mobile(self, ):
        return self.initial['eml']	
  
        
