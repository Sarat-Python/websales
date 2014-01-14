from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.db import models
from django.forms import ModelForm

from users.models import WebUser

# can be used at both admin and shopping sites
class BatchCreationForm(forms.Form):
    """
    A form that generates batch numbers per given range.
    """
    batch_number = forms.CharField(max_length=15)
    generate_range = forms.CharField(max_length=3)
    price = forms.IntegerField()
    
    
    