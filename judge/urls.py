from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('accounts/signup', views.UserCreate.as_view(), name='signup'),
    path('accounts/profile', views.UserProfile.as_view(), name='user_profile'),
    path('problems/', views.ProblemIndex.as_view(), name='problems_index'),
    path('problem/<slug:slug>', views.Problem.as_view(), name='problem'),
    path('problem/<slug:slug>/submit', views.ProblemSubmit.as_view(), name='problem_submit'),
    path('problem/<slug:slug>/submissions', views.ProblemAllSubmissions.as_view(), name='problem_all_submissions'),
    path('problem/<slug:slug>/rank', views.ProblemBestSubmissions.as_view(), name='problem_best_submissions'),
    path('callback/<str:uuid>', views.callback, name='callback'),
    path('users/', views.UserIndex.as_view(), name='users_index'),
    path('user/<slug:slug>', views.Profile.as_view(), name='profile'),
    path('user/<slug:slug>/submissions', views.UserSubmissions.as_view(), name='user_submissions'),
    path('accounts/profile/edit', views.ProfileUpdate.as_view(), name='profile_edit'),
    path('submissions/', views.SubmissionIndex.as_view(), name='submission_index'),
    path('submission/<int:pk>', views.Submission.as_view(), name='submission'),
]

