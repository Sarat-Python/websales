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

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.template.loader import render_to_string


# Create your views here.

def terms(request):
    termsdata = render_to_string('terms.html')    
    return HttpResponse(termsdata)

'''
def home(request):
    termsdata = render_to_string('home.html')    
    return HttpResponse(termsdata)


def about(request):
    termsdata = render_to_string('about.html')    
    return HttpResponse(termsdata)


def contact(request):
    termsdata = render_to_string('contact.html')    
    return HttpResponse(termsdata)
'''
