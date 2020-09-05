from django.views.generic.base import RedirectView
from django.views import View
from .. import forms
from django.views.generic import DetailView, ListView
from .. import models
from django.views.generic.edit import UpdateView, FormView
from django.urls import reverse_lazy
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.urls import reverse
from . import mixin

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

class UserIndex(ListView, mixin.TitleMixin, mixin.SidebarMixin):
    model = models.User
    context_object_name = 'users'
    template_name = 'judge/user_index.html'
    title = 'PNOJ: Users'

    def get_ordering(self):
        return '-points'

class Profile(DetailView, mixin.TitleMixin, mixin.SidebarMixin):
    model = models.User
    context_object_name = 'profile'
    template_name = "judge/profile.html"

    def get_slug_field(self):
        return 'username'

    def get_title(self):
        return 'PNOJ: User ' + self.get_object().username

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_contenttype = ContentType.objects.get_for_model(models.User)
        context['comments'] = models.Comment.objects.filter(parent_content_type=user_contenttype, parent_object_id=self.get_object().pk)
        return context

class UserSubmissions(ListView, mixin.TitleMixin, mixin.SidebarMixin):
    context_object_name = "submissions"
    template_name = 'judge/submission_list.html'
    paginate_by = 50

    def get_queryset(self):
        self.user = get_object_or_404(models.User, username=self.kwargs['slug'])
        return models.Submission.objects.filter(author=self.user).order_by(self.get_ordering())

    def get_ordering(self):
        return '-points'

    def get_title(self):
        return 'PNOJ: Submissions by User ' + self.user.username

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.kwargs['slug']
        context['purpose'] = 'user_submissions'
        return context

# class ProfileUpdate(UpdateView):
#     model = models.User
#     fields = ['description', 'timezone', 'main_language', 'organizations']
#     template_name = 'judge/profile_update_form.html'
#     success_url = reverse_lazy('user_profile')

#     def get_object(self):
#         return self.request.user

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
#         context['page_title'] = 'PNOJ: Update Profile'
#         return context

class ProfileUpdate(UpdateView, mixin.TitleMixin, mixin.SidebarMixin):
    template_name = 'judge/profile_update_form.html'
    form_class = forms.ProfileUpdateForm
    success_url = reverse_lazy('user_profile')
    title = 'PNOJ: Update Profile'

    def get_object(self):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super(UpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
