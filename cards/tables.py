

import django_tables2 as tables
#from cards.models import bulk_cards, generated_batch
from cards.models import SwipedCard

class SwipedCardTable(tables.Table):
    selection = tables.CheckBoxColumn(accessor="pk", attrs = { "th__input":
                                        {"onclick": "toggle(this)"}},
                                        orderable=False)
    class Meta:
        model = SwipedCard
        attrs = {'class': 'table'}
        fields = ('card_number', 'upc_code', 'amount',  'card_type', 'Activated', 'created_on')
        sequence = ('selection', 'card_type', 'card_number', 'upc_code', 'amount', 'Activated', 'created_on')
        
#class BulkCardTable(tables.Table):
#    
#    selection = tables.CheckBoxColumn(accessor="pk", attrs = { "th__input": 
#                                        {"onclick": "toggle(this)"}},
#                                        orderable=False)
#    
#    cost = tables.Column(orderable=False)
#    card_number = tables.Column(attrs= {"id":"pg_status"}, orderable=True)
#    
#    
#    class Meta:
#        model = bulk_cards
#        attrs = {'class': 'table'}
#        fields = ('card_number', 'cost') # fields to display
#        sequence = ('selection', 'card_number', 'cost')
#
#
#class BatchDisplayTable(tables.Table):
#    
#    selection = tables.CheckBoxColumn(accessor="batch_number", attrs = { "th__input": 
#                                        {"onclick": "toggle(this)"}},
#                                        orderable=False)
#    total_cost = tables.Column(verbose_name="product cost")
#    class Meta:
#        model = generated_batch
#        attrs = {'class': 'table'}
#        fields = ('batch_number', 'card_type', 'created_on','created_by', 'total_cost') # fields to display
#        sequence = ('selection', 'batch_number','card_type', 'created_on','created_by', 'total_cost')