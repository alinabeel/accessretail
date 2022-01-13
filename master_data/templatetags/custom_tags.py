import json
from django import template
from random import randint
register = template.Library()

@register.filter(name='jsonify')
def jsonify(data):
    if isinstance(data, dict):
        return data
    else:
        return json.loads(data)


@register.simple_tag
def setvar(val=None):
  return val



@register.simple_tag
def random_number():
    return randint(0,999)