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
def test_tag(field):
    return field.field.widget.attrs.get('long_text')
