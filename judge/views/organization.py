from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.base import RedirectView
from django.views.generic.edit import UpdateView
from .. import forms
from .. import models
from django.urls import reverse_lazy
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.db.models import Count

class OrganizationIndex(ListView):
    model = models.Organization
    context_object_name = 'organizations'
    template_name = 'judge/organization_index.html'

    def get_ordering(self):
        return '-name'

    def get_queryset(self):
        return super(OrganizationIndex, self).get_queryset().annotate(member_count=Count('member'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['page_title'] = 'PNOJ: Organizations'
        return context


class Organization(DetailView):
    model = models.Organization
    context_object_name = 'organization'
    template_name = "judge/organization.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['page_title'] = 'PNOJ: Organization ' + self.get_object().name
        user_contenttype = ContentType.objects.get_for_model(models.Organization)
        context['comments'] = models.Comment.objects.filter(parent_content_type=user_contenttype, parent_object_id=self.get_object().pk)
        context['member_count'] = models.User.objects.filter(organizations=self.get_object()).count()
        return context

class OrganizationMembers(ListView):
    model = models.Organization
    context_object_name = 'users'
    template_name = 'judge/user_index.html'

    def get_ordering(self):
        return '-username'

    def get_queryset(self):
        self.organization = get_object_or_404(models.Organization, slug=self.kwargs['slug'])
        return models.User.objects.filter(organizations=self.organization).order_by(self.get_ordering())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['page_title'] = 'PNOJ: Members of Organization ' + self.organization.name
        context['purpose'] = 'organization_members'
        context['organization'] = self.organization
        return context

