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
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect

from shopping.forms import BatchCreationForm
# Create your views here.

@csrf_protect
def activation_bulk(request):
    batch_form = BatchCreationForm()
    params = {'batch_form':batch_form}
    params.update(csrf(request))
    return render_to_response('bulk.html', params)
