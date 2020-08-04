from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.base import RedirectView
from django.views.generic.edit import UpdateView, CreateView, FormView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
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
        if self.request.user.is_authenticated:
            context['organization_requests'] = models.OrganizationRequest.objects.filter(organization=self.get_object(), user=self.request.user).order_by('-created')[:3]
        else:
            context['organization_requests'] = []
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

class OrganizationRequest(LoginRequiredMixin, CreateView):
    template_name = "judge/organization_form.html"
    model = models.OrganizationRequest
    fields = ['reason']

    def form_valid(self, form):
        form.instance.organization = self.get_object()
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_object(self):
        return models.Organization.objects.get(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['page_title'] = 'PNOJ: Request to join Organization ' + self.get_object().name
        context['organization'] = self.get_object()
        return context

class OrganizationJoin(LoginRequiredMixin, FormView):
    template_name = "judge/organization_form.html"
    form_class = forms.OrganizationJoinForm
    fields = ['access_code']

    def get(self, *args, **kwargs):
        if not self.get_object().is_private:
            self.success()
            return redirect(self.get_object())
        return super().get(*args, **kwargs)

    def success(self):
        self.request.user.organizations.add(self.get_object())

    def form_valid(self, form):
        self.success()
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        return self.get_object().get_absolute_url()

    def get_object(self):
        return models.Organization.objects.get(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['page_title'] = 'PNOJ: Join Organization ' + self.get_object().name
        context['organization'] = self.get_object()
        return context

    def get_form_kwargs(self, *args, **kwargs):
        cur_kwargs = super().get_form_kwargs(*args, **kwargs)
        cur_kwargs['organization'] = self.get_object()
        return cur_kwargs

class OrganizationLeave(LoginRequiredMixin, RedirectView):
    query_string = True
    pattern_name = 'organization'

    def get_redirect_url(self, *args, **kwargs):
        organization = get_object_or_404(models.Organization, slug=kwargs['slug'])
        self.request.user.organizations.remove(organization)
        return super().get_redirect_url(*args, **kwargs)
