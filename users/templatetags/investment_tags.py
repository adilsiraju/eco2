from django import template
from initiatives.models import Initiative, Company

register = template.Library()

@register.filter
def lookup(value, arg):
    if 'initiative' in arg:
        return Initiative.objects.get(id=value)
    elif 'company' in arg:
        return Company.objects.get(id=value)
    return None