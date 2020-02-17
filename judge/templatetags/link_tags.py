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
def user(username):
    url = user_url(username)
    return mark_safe('<a href="{0}">{1}</a>'.format(url, username))

@register.filter
def problem_url(slug):
    return reverse('problem', args=[slug])
 
@register.filter
def problem(slug):
    url = problem_url(slug)
    problem = models.Problem.objects.get(slug=slug)
    return mark_safe('<a href="{0}">{1}</a>'.format(url, problem.name))

@register.filter
def submission_url(pk):
    return reverse('submission', args=[pk])
 
@register.filter
def submission(pk):
    url = submission_url(pk)
    return mark_safe('<a href="{0}">#{1}</a>'.format(url, pk))
