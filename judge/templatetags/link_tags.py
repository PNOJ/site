import hashlib
import urllib
from django import template
from django.utils.safestring import mark_safe
from django.shortcuts import reverse
from judge import models
 
register = template.Library()
 
@register.filter
def user_url(username):
    return reverse('profile', args=[username])
 
@register.filter
def user(username, postfix=''):
    url = user_url(username)
    return mark_safe('<a href="{0}{1}">{2}</a>'.format(url, postfix, username))

@register.filter
def problem_url(slug):
    return reverse('problem', args=[slug])
 
@register.filter
def problem(slug, postfix=''):
    url = problem_url(slug)
    problem = models.Problem.objects.get(slug=slug)
    return mark_safe('<a href="{0}{1}">{2}</a>'.format(url, postfix, problem.name))

@register.filter
def submission_url(pk):
    return reverse('submission', args=[pk])
 
@register.filter
def submission(pk, postfix=''):
    url = submission_url(pk)
    return mark_safe('<a href="{0}{1}">#{2}</a>'.format(url, postfix, pk))

@register.filter
def comment_url(pk):
    return reverse('comment', args=[pk])
 
@register.filter
def comment(pk, postfix=''):
    url = comment_url(pk)
    return mark_safe('<a href="{0}{1}">#{2}</a>'.format(url, postfix, pk))

@register.filter
def post_url(slug):
    return reverse('blog_post', args=[slug])
 
@register.filter
def post(slug, postfix=''):
    url = post_url(slug)
    post_obj = models.BlogPost.objects.get(slug=slug)
    return mark_safe('<a href="{0}{1}">{2}</a>'.format(url, postfix, post_obj.title))
