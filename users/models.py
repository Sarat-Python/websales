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

from django.db import models
from django.utils import timezone
from django.utils.http import urlquote
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.template.loader import get_template
from django.template import Context
from django.conf import settings

# Create your models here.	


class WebUserManager(BaseUserManager):
	def _create_user(self, email, password,
					is_staff, is_superuser, first_name,
					last_name, mobile, mobile_model,
					unit, street, suburb, postcode, interest):
		"""
		Creates and saves a User with the given email and password.
		"""
		now = timezone.now()
		
		if not email:
			raise ValueError('User email must be set')
		elif not first_name:
			raise ValueError('User First Name must be set')
		elif not last_name:
			raise ValueError('User Last Name must be set')
		elif not mobile:
			raise ValueError('User Mobile Number must be set')
		email = self.normalize_email(email)
		user = self.model(email=email,first_name=first_name,
					 last_name=last_name, mobile=mobile,
					 mobile_model = mobile_model,
					 unit = unit, street = street, suburb = suburb,
					 postcode = postcode, interest = interest,
					 is_staff=is_staff, is_active=False,
					 is_superuser=is_superuser, last_login=now,
					 date_joined=now)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, email, password, first_name,
					last_name, mobile, mobile_model,
					unit, street, suburb, postcode , interest):
		return self._create_user(email, password, False, False, first_name, last_name, mobile,
								 mobile_model,
								 unit, street, suburb,
								 postcode, interest)

	def create_superuser(self, email, first_name, last_name, mobile, password, mobile_model ,
						unit, street , suburb,
						postcode, interest ):
		return self._create_user(email, first_name, last_name, mobile,
						password, True, True, mobile_model,
						unit, street , suburb ,
						postcode, interest)


class WebUser(AbstractBaseUser, PermissionsMixin):
	email = models.EmailField(_('email address'), max_length=254, unique=True)
	first_name = models.CharField(_('first name'), max_length = 30, blank = False)
	middle_name = models.CharField(_('middle name'), max_length = 50, blank = True)
	last_name = models.CharField(_('last name'), max_length = 50, blank = False)
	mobile = models.CharField(_('mobile'), max_length = 20, blank = False)
	mobile_model = models.CharField(_('mobile model'), max_length = 30, blank = True)
	unit = models.CharField(_('unit'), max_length=10, blank = True)
	street = models.CharField(_('street'), max_length = 30, blank = True)
	suburb = models.CharField(_('suburb'), max_length = 30, blank = True)
	postcode = models.CharField(_('post code'), max_length = 10, blank = True)
	interest = models.TextField(_('interest'), blank = True)
	activation_code = models.CharField(max_length = 15, blank = True)
	
	is_staff = models.BooleanField(_('staff status'), default=False,
		help_text=_('Designates whether the user can log into this admin '
		'site.'))
	is_active = models.BooleanField(_('active'), default=False,
		help_text=_('Designates whether this user should be treated as '
		'active. Unselect this instead of deleting accounts.'))
	date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

	objects = WebUserManager()
	

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['first_name', 'last_name', 'mobile' ]
	
	def __unicode__(self):
		return self.email
	
	class Meta:
		verbose_name = _('user')
		verbose_name_plural = _('users')
	
	def get_absolute_url(self):
		return "/users/%s/" % urlquote(self.email)
		
	def get_full_name(self):
		"""
		Returns the first_name plus the last_name, with a space in between.
		"""
		full_name = '%s %s' % (self.first_name, self.last_name)
		return full_name.strip()
	
	def get_short_name(self):
		"Returns the short name for the user."
		return self.first_name
		
	#def send_activation_email(self):
		
	
	def email_user(self, subject, message, from_email=None):
		"""
		Sends an email to this User.
		"""
		send_mail(subject, message, from_email, [self.email])
		
		
	def send_activation_email(self):
		full_name = self.get_full_name()
		activation_code = self.activation_code
		subject = settings.ACTIVATION_EMAIL_SUBJECT
		expiry_days = settings.ACTIVATION_EXPIRY_DAYS
		removal_days = settings.ACCOUNT_REMOVAL_DAYS
		contents = get_template('activation_email.html').render(Context({
				'full_name': full_name,
				'activation_code': activation_code,
				'expiry_days': expiry_days,
				'remove_days': removal_days
			}))
		from_email = settings.ACTIVATION_ADMIN_EMAIL
		print(contents)
		send_mail(subject,contents,from_email,[self.email])
		
	def activate(self, user_code=None):
		if user_code is not None:			
			if user_code == self.activation_code:				
				self.is_active = 1				
				try:
					self.save()
					return True
				except:
					return False				
			else:
				return False



