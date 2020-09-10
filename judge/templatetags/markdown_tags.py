import requests
import markdown as markdown_pkg

from django import template
from django.utils.safestring import mark_safe
 
register = template.Library()
 
@register.filter
def markdown(markdown_content):
    html = markdown_pkg.markdown(
        markdown_content,
        extensions=['extra', 'nl2br', 'sane_lists'],
    )
    return mark_safe(html)
