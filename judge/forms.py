from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import get_user_model

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

