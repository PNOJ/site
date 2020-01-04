from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model
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

def profile():
    pass

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

def problems_index():
    pass

def problem():
    pass

def problem_submit():
    pass

def users_index():
    pass

def user():
    pass

def user_submission():
    pass

def submissions_index():
    pass

def submission():
    pass
