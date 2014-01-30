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

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.context_processors import csrf
from django.template import RequestContext
from django.contrib.auth import authenticate
from django.contrib.auth import login as dj_login, logout as dj_logout
from django.views.decorators.csrf import csrf_protect
from django.conf import settings

from recaptcha.client import captcha

from users.models import WebUser
from users.forms import WebUserCreationForm, WebUserChangeForm, WebPasswordChangeForm
from users.forms import ActivationForm
from users.utils import helpers

# Create your views here.
@csrf_protect
def login(request):
	if request.method == 'POST':
		if request.POST['submit'] == 'register':
			return HttpResponseRedirect('/user/register/')
		email = request.POST['email']
		password = request.POST['password']
		user = authenticate(email = email, password = password)
		if user is not None:
			if user.is_active:
				dj_login(request, user)
				full_name = user.get_full_name()
				request.session['email'] = email
				params = {'full_name':full_name}
				params.update(csrf(request))
				return HttpResponseRedirect('/cards/bulk/purchase/', params)
			else:
				return login_handler(request,'Account Inactive! Please activate your account')
		else:
			return HttpResponseRedirect("/user/invalid/")
		
	return render(request, 'login.html')


def logout(request):				
	dj_logout(request)
	return HttpResponseRedirect('/')

@csrf_protect
def loggedin(request):
	return render(request, 'loggedin.html')
	
def invalid(request):
	return render(request, 'invalid.html')
	
@csrf_protect
def register(request):	
	if request.user != None and request.user.is_authenticated():
		return HttpResponseRedirect('/user/loggedin/')
	captcha_public_key = settings.RECAPTCHA_PUBLIC_KEY
	response_dict = {'cpkey':captcha_public_key}
	if request.method == 'POST':		
		webuser_form = WebUserCreationForm(request.POST)
		#print(helpers.activation_code(request.POST.get('email')))
		
		# reCaptcha verification to prevent autobots
		response = captcha.submit(  
					request.POST.get('recaptcha_challenge_field'),  
					request.POST.get('recaptcha_response_field'),  
					settings.RECAPTCHA_PRIVATE_KEY,  
					request.META['REMOTE_ADDR'],)
		# testing - response
		# print(response.is_valid)
		if not response.is_valid:
			response_dict.update({'captcha_response': 'Please retry captcha input!'})
			response_dict.update({'f':webuser_form})
			print('invalid captcha')
			return render(request, 'register.html', response_dict)
		
		# create user in inactive status
		if webuser_form.is_valid():
			#print('coming before save')
			webuser_form.save()
			
			# generate and email activation code to user
			inactive_user = WebUser.objects.get(email=webuser_form.cleaned_data['email'])
			activation_code = helpers.activation_code(inactive_user.email)
			inactive_user.activation_code = activation_code
			inactive_user.save()
			inactive_user.send_activation_email()
			
			# send the email for immediate activation
			activation_form = ActivationForm(initial={'email':inactive_user.email})
			return render(request, 'activate.html', {'aform':activation_form, 'just_registered':True})
		else:
			response_dict.update({'f':webuser_form})
			return render(request, 'register.html', response_dict)
	else:
		register_form = WebUserCreationForm()
		response_dict.update({'f':register_form})
		return render(request, 'register.html',response_dict)

def activate(request):
	if request.user != None and request.user.is_authenticated():
		return HttpResponseRedirect('/cards/bulk/purchase/')
	if request.method == 'POST':
		request_form = ActivationForm(request.POST)
		if request_form.is_valid():
			inactive_user = None
			try:
				inactive_user = WebUser.objects.get(email=request_form.cleaned_data['email'])
			except WebUser.DoesNotExist:
				response_dict = {
					'msg':'Email not found! Please register to activate',
					'aform':ActivationForm()}
				return render(request,'activate.html',response_dict)
			if inactive_user.is_active == 1:
				activation_form = ActivationForm()
				msg = 'Account is already activated! Please login'
				return render(request, 'activate.html',{'msg':msg,'aform':activation_form})
			if inactive_user.activate(request_form.cleaned_data['activation_code']):
				# auto authenticate
				inactive_user.backend = "django.contrib.auth.backends.ModelBackend"
				dj_login(request, inactive_user)
				return HttpResponseRedirect('/cards/bulk/purchase/')
			else:
				response_dict = {
					'aform':request_form,
					'msg':'Invalid activation code! Please regenerate'
					}
				return render(request,'activate.html',response_dict)
		else:
			return render(request, 'activate.html', {'aform':request_form})
	else:
		activation_form = ActivationForm()
		return render(request, 'activate.html', {'aform':activation_form})

def register_response(request):
	return render(request, 'response.html')

@csrf_protect
def change_password(request):
	if is_loggedin(request):
		if request.method == 'POST':
			change_form = WebPasswordChangeForm(request.POST)
			if change_form.is_valid():					
				old = change_form.cleaned_data['old_password']
				email = request.session['email']
				user = authenticate(email = email, password = old)			
				if user:
					newp = change_form.cleaned_data['password1']
					user.set_password(newp)
					user.save()
					return HttpResponseRedirect('/user/loggedin/', {'error': 'Password changed successfully'})
				else:
					return HttpResponseRedirect('/user/loggedin/', {'error':'Unable to update, Please try again later'})
			else:
				return render(request, 'change_password.html', {'change_form':change_form, 'error':'password mismatch'})
		else:
			change_form = WebPasswordChangeForm()
			xss_safe = {'change_form':change_form}
			xss_safe.update(csrf(request))
			return render(request, 'change_password.html', xss_safe)
	else:
		return login_handler(request,'Login to change password!')

def is_loggedin(request):
	if request.user != None and request.user.is_authenticated():
		return True
	else:
		return login_handler(request,'Login to continue')

def login_handler(request, error):
		return render(request, 'login.html', {'error': error})
	
