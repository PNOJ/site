from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('post/<slug:slug>', views.BlogPost.as_view(), name='blog_post'),
    path('accounts/signup', views.UserCreate.as_view(), name='signup'),
    path('accounts/profile', views.UserProfile.as_view(), name='user_profile'),
    path('problems/', views.ProblemIndex.as_view(), name='problems_index'),
    path('problem/<slug:slug>', views.Problem.as_view(), name='problem'),
    path('problem/<slug:slug>/submit', views.ProblemSubmit.as_view(), name='problem_submit'),
    # path('problem/<slug:slug>/resubmit/<int:submission_pk>', views.ProblemReSubmit.as_view(), name='problem_resubmit'),
    path('problem/<slug:slug>/submissions', views.ProblemAllSubmissions.as_view(), name='problem_all_submissions'),
    path('problem/<slug:slug>/rank', views.ProblemBestSubmissions.as_view(), name='problem_best_submissions'),
    path('callback/<str:uuid>', views.callback, name='callback'),
    path('passthrough/<str:uuid>', views.passthrough, name='passthrough'),
    path('users/', views.UserIndex.as_view(), name='users_index'),
    path('user/<str:slug>', views.Profile.as_view(), name='profile'),
    path('user/<str:slug>/submissions', views.UserSubmissions.as_view(), name='user_submissions'),
    path('organizations/', views.OrganizationIndex.as_view(), name='organizations_index'),
    path('organization/<str:slug>', views.Organization.as_view(), name='organization'),
    path('organization/<str:slug>/members', views.OrganizationMembers.as_view(), name='organization_members'),
    path('accounts/profile/edit', views.ProfileUpdate.as_view(), name='profile_edit'),
    path('submissions/', views.SubmissionIndex.as_view(), name='submission_index'),
    path('submission/<int:pk>', views.Submission.as_view(), name='submission'),
    path('submission/<int:pk>/source', views.SubmissionSource.as_view(), name='submission_source'),
    path('submission/<int:pk>/data', views.get_submission_data, name='submission_data'),
    path('comment/<int:pk>', views.Comment.as_view(), name='comment'),
    path('<str:parent_type>/<slug:parent_id>/add_comment', views.add_comment, name='add_comment'),
]

