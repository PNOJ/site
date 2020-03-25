import requests
import markdown as markdown_pkg

from django import template
from django.utils.safestring import mark_safe
 
register = template.Library()
 
# @register.filter
# def markdown(markdown_content, mode="gfm"):
#     post_content = {'text': markdown_content, 'mode': mode, 'context': 'pnoj/site'}
#     rendered_markdown = requests.post("https://api.github.com/markdown", json=post_content)
#     rendered_markdown.raise_for_status()
#     return mark_safe(rendered_markdown.text)

@register.filter
def markdown(markdown_content):
    html = markdown_pkg.markdown(markdown_content)
    return mark_safe(html)
