from django import template

register = template.Library()

@register.filter(name='styleclass')
def style_class(value, arg):
    return value.as_widget(attrs={'class': arg})