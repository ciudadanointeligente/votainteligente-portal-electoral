import datetime
from django import template

register = template.Library()

@register.simple_tag
def hide_tag(field):
    aux="hide"
    if field.field.widget.attrs.get('visible'):
        aux=""
    return aux

@register.simple_tag
def long_text_tag(field):
    return field.field.widget.attrs.get('long_text')


@register.simple_tag
def tab_text_tag(field):
    return field.field.widget.attrs.get('tab_text')
