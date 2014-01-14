from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.template.loader import render_to_string


# Create your views here.

def terms(request):
    termsdata = render_to_string('terms.html')    
    return HttpResponse(termsdata)

