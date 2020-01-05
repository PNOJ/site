import requests
from django import template
from django.utils.safestring import mark_safe
 
register = template.Library()
 
# return an image tag with the gravatar
# TEMPLATE USE:  {{ email|gravatar:150 }}
@register.filter
def markdown(markdown_content, mode="gfm"):
    post_content = {'text': markdown_content, 'mode': mode, 'context': 'pnoj/site'}
    rendered_markdown = requests.post("https://api.github.com/markdown", json=post_content)
    rendered_markdown.raise_for_status()
    return mark_safe(rendered_markdown.text)
