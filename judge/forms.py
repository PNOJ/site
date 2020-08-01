from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm
from django import forms
from django.db.models import Q

from . import models

from allauth.account.forms import SignupForm
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible

User = get_user_model()

class RegisterForm(UserCreationForm):
    username = forms.CharField(label="Your Username")
    password1 = forms.CharField(label="Your Password", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Repeat Your Password", widget=forms.PasswordInput())
    email = forms.EmailField(label = "Email Address")
 
    class Meta:
        model = User
        fields = ("email", "username", "password1", "password2")
 
    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
 
        if commit:
            user.save()
            return user

class PNOJSignupForm(SignupForm):
    captcha = ReCaptchaField()

class ProfileUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ['description', 'timezone', 'main_language', 'organizations']
        widgets = {
            'organizations': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        if not user.has_perm('judge.edit_all_organization'):
            self.fields['organizations'].queryset = models.Organization.objects.filter(Q(is_private=False) | Q(admins=user) | Q(pk__in=user.organizations.all())).distinct()
        self.initial['organizations'] = [i.pk for i in user.organizations.all()]
