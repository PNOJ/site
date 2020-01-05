from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import views as auth_views
from django.views import View
from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.base import RedirectView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy
from . import models
from . import forms

# Create your views here.

User = get_user_model()

class Index(TemplateView):
    template_name = 'judge/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        return context

class UserProfile(RedirectView):
    permanent = False
    query_string = False
    pattern_name = "profile"

    def get_redirect_url(self, *args, **kwargs):
        user = self.request.user
        return reverse(self.pattern_name, args=[user.username])

class UserCreate(View):
    form_class = forms.RegisterForm
    template_name = 'registration/signup.html'

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = User.objects.create_user(form.cleaned_data['username'], form.cleaned_data['email'], form.cleaned_data['password1'])
            return redirect("login")

        return render(request, self.template_name, {'form': form})

class ProblemIndex(ListView):
    model = models.Problem
    context_object_name = 'problems'
    template_name = 'judge/problem_index.html'

    def get_ordering(self):
        return 'name'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        return context

class Problem(DetailView):
    model = models.Problem
    context_object_name = 'problem'
    template_name = "judge/problem.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        return context

def problem_submit():
    pass

class UserIndex(ListView):
    model = models.User
    context_object_name = 'users'
    template_name = 'judge/user_index.html'

    def get_ordering(self):
        return 'points'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        return context


class Profile(DetailView):
    model = models.User
    context_object_name = 'profile'
    template_name = "judge/profile.html"

    def get_slug_field(self):
        return 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        return context


def user_submission():
    pass

class ProfileUpdate(UpdateView):
    model = models.User
    fields = ['description', 'timezone', 'main_language', 'organizations']
    template_name = 'judge/profile_update_form.html'
    success_url = reverse_lazy('user_profile')

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        return context



def submissions_index():
    pass

def submission():
    pass
