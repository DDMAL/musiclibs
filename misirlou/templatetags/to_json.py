import ujson as json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
def to_json(data):
    """Serialize data as JSON"""
    return mark_safe(json.dumps(data))
