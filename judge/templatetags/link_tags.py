import hashlib
import urllib
from django import template
from django.utils.safestring import mark_safe
from django.shortcuts import reverse
from judge import models
import django.contrib.humanize.templatetags.humanize as humanize
 
register = template.Library()
 
@register.filter
def user_url(username):
    return reverse('user_detail', args=[username])
 
@register.filter
def user(username, postfix=''):
    url = user_url(username)
    return mark_safe('<a href="{0}{1}">{2}</a>'.format(url, postfix, username))

@register.filter
def users(usernames, postfix=''):
    users_string = ', '.join([user(username, postfix) for username in usernames])
    return mark_safe(users_string)

@register.filter
def problem_url(slug):
    return reverse('problem_detail', args=[slug])
 
@register.filter
def problem(slug, postfix=''):
    url = problem_url(slug)
    problem = models.Problem.objects.get(slug=slug)
    return mark_safe('<a href="{0}{1}">{2}</a>'.format(url, postfix, problem.name))

@register.filter
def submission_url(pk):
    return reverse('submission_detail', args=[pk])
 
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

def comment_info(comment_obj):
    parent_type = comment_obj.parent_content_type.model
    if parent_type == 'problem':
        parent_url = problem(comment_obj.parent.slug)
    elif parent_type == 'submission':
        parent_url = "Submission " + submission(comment_obj.parent.pk)
    elif parent_type == 'user':
        parent_url = user(comment_obj.parent.username)
    elif parent_type == 'comment':
        parent_url = "Comment " + comment(comment_obj.parent.pk)
    elif parent_type == 'blogpost':
        parent_url = post(comment_obj.parent.slug)
    elif parent_type == 'organization':
        parent_url = organization(comment_obj.parent.slug)
    else:
        parent_url = "unknown."
    comment_url = comment(comment_obj.pk)
    author_url = user(comment_obj.author.username)
    comment_date = humanize.naturaltime(comment_obj.created_date)
    return comment_url, author_url, comment_date, parent_url

@register.filter
def comment_html_nodate(comment_obj):
    comment_url, author_url, comment_date, parent_url = comment_info(comment_obj)
    return mark_safe("{0}: {1} commented on {2}".format(comment_url, author_url, parent_url))

@register.filter
def comment_html(comment_obj):
    comment_url, author_url, comment_date, parent_url = comment_info(comment_obj)
    return mark_safe("{0}: {1} commented {2} on {3}".format(comment_url, author_url, comment_date, parent_url))

@register.filter
def post_url(slug):
    return reverse('blog_post', args=[slug])
 
@register.filter
def post(slug, postfix=''):
    url = post_url(slug)
    post_obj = models.BlogPost.objects.get(slug=slug)
    return mark_safe('<a href="{0}{1}">{2}</a>'.format(url, postfix, post_obj.title))

@register.filter
def organization_url(slug):
    return reverse('organization_detail', args=[slug])
 
@register.filter
def organization(slug, postfix=''):
    url = organization_url(slug)
    organization_obj = models.Organization.objects.get(slug=slug)
    return mark_safe('<a href="{0}{1}">{2}</a>'.format(url, postfix, organization_obj.name))
