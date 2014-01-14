# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.context_processors import csrf
from django.contrib.auth import login as dj_login, logout as dj_logout
from django.views.decorators.csrf import csrf_protect
from datetime import datetime
from django.forms.formsets import formset_factory

from django.conf import settings

#from cards.forms import GenerateBulkCardsForm, EditBulkCardsForm
from cards.forms import SwipedCardForm, UpdateSwipedCardForm, UpdateFormSet
from cards.models import SwipedCard, Batch
import card_utils
import tables
from django_tables2 import RequestConfig
from users.models import WebUser
#from cards.models import generated_batch

def bulk(request):
    form = SwipedCardForm(request.POST or None)
    response_dict = {'form':form}
    batch_number = request.session.get('batch_number', False)
    print batch_number
    email = request.user
    if not batch_number:
        print 'batch number not present: fresh request'
        batch_number = datetime.now().isoformat()
       
        try:
            batch = Batch.objects.get(batch_number = batch_number, created_by = email)
        except Batch.DoesNotExist:
            print 'creating new batch %s' % batch_number
            user = WebUser.objects.get(email=email)
            total = 0
            batch = Batch(batch_number = batch_number,
                      created_by = user,
                      assigned_to = user,                      
                      total_cost = total
                      )
            batch.save()
            #form = SwipedCardForm(initial={'batch_id':batch.id})
            #form.batch = batch
            #print 'batch saved %s' % (form.batch)
            #print batch_number
            request.session['batch_number'] = batch_number
    else:
        #print batch_number
        batch = Batch.objects.get(batch_number = batch_number)
        if form.is_valid():
            #print 'form is valid'
            cleaned_card = card_utils.extract_card_number(form.cleaned_data.get('card_number'),
                                                          form.cleaned_data.get('card_type'))
            upc_code = card_utils.extract_upc_code(cleaned_card,
                                                   form.cleaned_data.get('card_type'))
            submitted = form.save(commit=False)
            submitted.card_number = cleaned_card
            submitted.upc_code = upc_code                        
            submitted.batch_id = batch.id
            print cleaned_card, upc_code
            print submitted.verify_card_number()
            if submitted.verify_card_number():
                submitted.save()
                print batch.total_cost+submitted.amount
                batch.total_cost = batch.total_cost+ submitted.amount
                batch.save()
                print submitted.card_number
                form = SwipedCardForm(initial={'card_type':submitted.card_type,
                                           'amount':submitted.amount,'card_focus':'on'})
            response_dict.update({'form':form})
            
        else:
            print 'invalid form'
        response_dict.update({'batch_total':batch.total_cost})
        new_cards = SwipedCard.objects.filter(batch_id=batch.id, deleted=False)
        table = tables.SwipedCardTable(new_cards)
        RequestConfig(request,paginate={"per_page": 15}).configure(table)
        response_dict.update({'table':table})
    return render(request,'web_purchase.html', response_dict)

def update(request):
    
    if request.method == 'POST':
        selected = request.POST.getlist('selection', None)
        form_set  = SwipedCardForm()
        action = request.POST.get('action')
        response_dict ={'formset':form_set}
        print request.session['batch_number']
        
        if action == 'save':
            formset = UpdateFormSet(request.POST)
            for form in formset.forms:
                form.save()
                print 'form saved'
            return HttpResponseRedirect('/cards/bulk/purchase/')
        
        if action == 'delete':
            batch_number = request.session['batch_number']
            batch = Batch.objects.get(batch_number = batch_number)
            form_set = UpdateFormSet(queryset = SwipedCard.objects.filter(pk__in=selected, deleted=False))
            for form in form_set.forms:
                submitted = form.save(commit=False)
                submitted.deleted = True
                submitted.save()
                batch.total_cost = batch.total_cost - submitted.amount
                batch.save()
                print 'form saved'
            response_dict={'batch_total': batch.total_cost}
            return HttpResponseRedirect('/cards/bulk/purchase/', response_dict)

        form_set = UpdateFormSet(queryset = SwipedCard.objects.filter(pk__in=selected, deleted=False))
        response_dict ={'formset':form_set}

    return render(request, 'update_cards.html', response_dict)

 #UpdateCardForms = formset_factory(UpdateSwipedCardForm, extra=len(selected))
            #formset =UpdateCardForms()
            #if formset.is_valid():
            #    for form in formset.form():
            #        form.card_number = card.card_number
                #form = UpdateSwipedCardForm(instance=card)
#
#def bulk_generate(request):
#    form = GenerateBulkCardsForm(request.POST or None)
#    response_dict = {'form':form}
#    if form.is_valid():
#        print request.session['email']
#        form.save_generated_cards(request.session['email'])
#        request.session['batch_number'] = form.cleaned_data['batch_number']        
#    else:
#        msg = "Invalid details! Please retry"
#        print msg
#        response_dict.update({'msg':msg})
#        
#    if request.session.get('batch_number', False):
#        batch_number = request.session.get('batch_number')
#        new_cards = card_utils.get_cards_for_batch(batch_number)
#        card_type = generated_batch.objects.get(batch_number=batch_number).card_type
#        response_dict.update({'card_type':card_type})
#        table = tables.BulkCardTable(new_cards)
#        RequestConfig(request, paginate={"per_page": 15}).configure(table)
#        response_dict.update({'table':table})
#    
#    return render(request, 'generate.html',response_dict)
#
#def bulk_edit(request):
#    if request.method == 'POST':
#        selected = request.POST.getlist('selection', None)
#        if selected != None:
#            form = EditBulkCardsForm(request.POST or None, extra=selected)
#            return render(request, 'edit.html',{'form':form})        
#    form = GenerateBulkCardsForm()        
#    return render(request,'generate.html',{'form':form})
#
#def bulk_update(request):
#    if request.method == 'POST':
#        card_utils.update_card_details(request)     
#    return HttpResponseRedirect('/cards/bulk/generate/')

def purchase(request):
    if request.method == 'POST':
        #email = request.user
        #print email
        #batch_list = card_utils.get_batch_for_user(email)
        #table = tables.BatchDisplayTable(batch_list)
        #print (table==None)
        #RequestConfig(request,paginate={"per_page":15}).configure(table)
        #response_dict = {'table' : table}
        #batch_number = request.POST.get('batch', None)
        #search_number = request.POST.get('search', None)
        #
        #print 'before batch'
        #print batch_number, search_number
        #
        #if batch_number:
        #    pass
        #
        #if search_number:
            pass
        
    return render(request,'purchase.html', response_dict)
    
        
    
        
        
    