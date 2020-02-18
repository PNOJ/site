from django import template
from django.utils.safestring import mark_safe
from django.shortcuts import reverse
from judge import models
 
register = template.Library()
 
@register.filter
def startswith(string, substring):
    return string.startswith(substring)

@register.filter
def split(string, split_char=" "):
    return string.split(split_char)
