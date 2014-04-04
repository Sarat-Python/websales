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
  Story #27    Task #28   Sarat      04/04/2014   Added Select Venue 
                                                  during registration.
 End Change Log ***************************************************************
'''

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField
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
    #password = forms.CharField(widget=forms.PasswordInput(render_value=False))
    #retype_password = forms.CharField(widget=forms.PasswordInput(render_value=False))
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
    #venue = forms.CharField(widget=forms.Select(choices=kiosk_venues.objects.values('name').filter(is_deleted=0).values_list('id','name')), required = True)
    
    class Meta:
        model = WebUser
        fields = ("email", "first_name",
                  "middle_name", "last_name", "mobile", "mobile_model",
                  "unit", "street", "suburb", "postcode", "interest","venue")
    
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
	#self.fields['venue'].choices.insert(0, ('','Select Venue' ) )
        
    def clean_email(self):
        email = self.cleaned_data['email']
        if WebUser.objects.filter(email=email).exists():
            raise ValidationError(_("Email is already registered"), code='registered')
        return email
    
    #def clean_retype_password(self):
    #    password = self.cleaned_data.get('password')
    #    retype_password = self.cleaned_data.get('retype_password')
    #    if password and retype_password and password != retype_password:
    #        raise forms.ValidationError(_("Entered password don't match!"), code='password_mismatch')
    #    return retype_password
    
    #def clean_first_name(self):
    #    first_name = self.cleaned_data['first_name']
    #    if not first_name:
    #        raise ValidationError(_("Please enter your first name"), code='blank_first_name')
    #    return first_name
    #
    #def clean_last_name(self):
    #    last_name = self.cleaned_data['last_name']
    #    if not last_name:
    #        raise ValidationError(_("Please enter your last name"), code='blank_last_name')
    #    return last_name
    #
    #def clean_mobile(self):
    #    mobile = self.cleaned_data['mobile']
    #    if not mobile:
    #        raise ValidationError(_("Please enter your mobile number"), code='blank_mobile')
    #    return mobile    
    
   

        
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
    old_password = forms.CharField(widget=forms.PasswordInput(render_value=False))
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False))
     
    class Meta:
        model = WebUser
        fields = ('email',)
        #fields = ["first_name",
        #          "middle_name", "last_name", "mobile", "mobile_model",
        #          "unit", "street", "suburb", "postcode", "interest"]
    
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            msg = "Passwords don't match"
            raise forms.ValidationError(msg)
        return password2
    
    #def save(self, commit=True):
    #    # Save the provided password in hashed format
    #    user = super(WebUserChangeForm,
    #                    self).save(commit=False)
    #    user.set_password(self.cleaned_data["password1"])
    #    if commit:
    #        user.save()
    #    return user
    
    #def clean_password(self, ):
    #    return self.initial['password']

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
    
