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
