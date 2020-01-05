from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('accounts/signup', views.UserCreate.as_view(), name='signup'),
    path('accounts/profile', views.UserProfile.as_view(), name='user_profile'),
    path('problems/', views.problems_index, name='problems_index'),
    path('problem/<slug:name>', views.problem, name='problem'),
    path('problem/<slug:name>/submit', views.problem_submit, name='problem_submit'),
    path('users/', views.UserIndex.as_view(), name='users_index'),
    path('user/<slug:slug>', views.Profile.as_view(), name='profile'),
    path('user/<slug:slug>/submissions', views.user_submission, name='user_submissions'),
    path('accounts/profile/edit', views.ProfileUpdate.as_view(), name='profile_edit'),
    path('submissions/', views.submissions_index, name='submission_index'),
    path('submission/<int:id>', views.submission, name='index'),
]

