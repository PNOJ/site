from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('accounts/signup', views.UserCreate.as_view(), name='signup'),
    path('accounts/profile', views.profile, name='profile'),
    path('problems/', views.problems_index, name='problems_index'),
    path('problem/<slug:name>', views.problem, name='problem'),
    path('problem/<slug:name>/submit', views.problem_submit, name='problem_submit'),
    path('users/', views.users_index, name='users_index'),
    path('user/<slug:name>', views.user, name='user'),
    path('user/<slug:name>/submissions', views.user_submission, name='user_submissions'),
    path('submissions/', views.submissions_index, name='submission_index'),
    path('submission/<int:id>', views.submission, name='index'),
]

