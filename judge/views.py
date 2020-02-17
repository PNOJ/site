from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import views as auth_views
from django.views import View
from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.base import RedirectView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from . import models
from . import forms
from pnoj import settings
import uuid
import json
import logging
from pnoj.settings import k8s
from pnoj.settings import k8s_config

# Create your views here.

User = get_user_model()
logger = logging.getLogger('django')

class Index(TemplateView):
    template_name = 'judge/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['page_title'] = 'PNOJ'
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
        context['page_title'] = 'PNOJ: Problems'
        return context

class Problem(DetailView):
    model = models.Problem
    context_object_name = 'problem'
    template_name = "judge/problem.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['page_title'] = 'PNOJ: ' + self.get_object().name
        return context

def create_judge_job(submission_id, problem_file_url, submission_file_url, callback_url, language, memory_limit):
    # Configureate Pod template container
    resource = k8s.client.V1ResourceRequirements(limits={'memory': str(memory_limit) + "Mi", 'cpu': settings.cpu_limit})
    container = k8s.client.V1Container(
        name="judge-container-{0}".format(submission_id),
        image=settings.languages[language]['docker_image'],
        args=['--submission_file_url', submission_file_url, '--problem_file_url', problem_file_url, '--callback_url', callback_url],
        resources=resource)
    # Create and configurate a spec section
    template = k8s.client.V1PodTemplateSpec(
        metadata=k8s.client.V1ObjectMeta(labels={"app": "pnoj"}),
        spec=k8s.client.V1PodSpec(restart_policy="Never", containers=[container], runtime_class_name="gvisor"))
        # spec=k8s.client.V1PodSpec(restart_policy="Never", containers=[container]))
    # Create the specification of deployment
    spec = k8s.client.V1JobSpec(
        template=template,
	active_deadline_seconds=1800,
	ttl_seconds_after_finished=3600,
        backoff_limit=4)
    # Instantiate the job object
    job = k8s.client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=k8s.client.V1ObjectMeta(name="judge-job-{0}".format(submission_id)),
        spec=spec)

    api_instance = k8s.client.BatchV1Api(k8s.client.ApiClient(k8s_config))
    api_response = api_instance.create_namespaced_job(
        body=job,
        namespace="pnoj")

@method_decorator(login_required, name='dispatch')
class ProblemSubmit(CreateView):
    template_name = 'judge/problem_submit.html'
    model = models.Submission
    fields = ('source', 'language')

    def form_valid(self, form, **kwargs):
        model = form.save(commit=False)
        model.author = self.request.user
        model.problem = models.Problem.objects.get(slug=self.kwargs['slug'])
        model.status = 'G'
        model.save()

        callback_uuid = uuid.uuid4().hex
        cache.set('callback-{0}'.format(callback_uuid), model.pk, 1800)
        callback_url = self.request.build_absolute_uri(reverse('callback', kwargs={'uuid': callback_uuid}))
        submission_file_url = self.request.build_absolute_uri(model.source.url)
        problem_file_url = self.request.build_absolute_uri(model.problem.problem_file.url)
        if hasattr(settings, 'override_callback_url'):
            logger.info("Callback url for submission #{0}: {1}".format(model.pk, callback_url))
            callback_url = settings.override_callback_url.format(callback_uuid)
        if hasattr(settings, 'override_submission_file_url'):
            logger.info("Submission file url for submission #{0}: {1}".format(model.pk, submission_file_url))
            submission_file_url = settings.override_submission_file_url.format(model.problem.slug, model.language)
        if hasattr(settings, 'override_problem_file_url'):
            logger.info("Problem file url for submission #{0}: {1}".format(model.pk, problem_file_url))
            problem_file_url = settings.override_problem_file_url.format(model.problem.slug)
        create_judge_job(model.pk, problem_file_url, submission_file_url, callback_url, model.language, model.problem.memory_limit * 2)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['problem'] = models.Problem.objects.get(slug=self.kwargs['slug'])
        context['page_title'] = 'PNOJ: Submit to ' + self.get_object().name
        return context

@csrf_exempt
def callback(request, uuid):
    submission_pk = cache.get("callback-{0}".format(uuid))

    result = json.loads(request.body)

    logger.info(result)

    submission = models.Submission.objects.get(pk=submission_pk)
    submission.scored = result['score']['scored']
    submission.scoreable = result['score']['scoreable']
    submission.points = (result['score']['scored']/result['score']['scoreable'])*submission.problem.points
    submission.status = result['status']
    if 'resource' in result:
        submission.time = result['resource']['time']
        submission.memory = result['resource']['memory']
    if 'data' in result and not result['data'] == None:
        submission.message = result['data']

    submission.save()

    for batch_result in result['batches']:
        batch = models.SubmissionBatchResult()
        batch.name = batch_result['name']
        batch.submission = submission
        if 'data' in batch_result and not batch_result['data'] == None:
            batch.message = batch_result['data']
        batch.scored = batch_result['score']['scored']
        batch.scoreable = batch_result['score']['scoreable']
        batch.status = batch_result['status']
        if 'resource' in batch_result:
            batch.time = batch_result['resource']['time']
            batch.memory = batch_result['resource']['memory']
        batch.save()
        for testcase_result in batch_result['testcases']:
            testcase = models.SubmissionTestcaseResult()
            testcase.name = testcase_result['name']
            testcase.submission = submission
            testcase.batch = batch
            if 'data' in batch_result and not batch_result['data'] == None:
                # testcase.message = testcase_result['data']
                pass
            testcase.status = testcase_result['status']
            if 'resource' in testcase_result:
                testcase.time = testcase_result['resource']['time']
                testcase.memory = testcase_result['resource']['memory']
            testcase.save()

    submission.author.save()
    return HttpResponse("OK")

class ProblemAllSubmissions(ListView):
    context_object_name = "submissions"
    template_name = 'judge/submission_list.html'
    paginate_by = 50

    def get_queryset(self):
        self.problem = get_object_or_404(models.Problem, slug=self.kwargs['slug'])
        return models.Submission.objects.filter(problem=self.problem).order_by(self.get_ordering())

    def get_ordering(self):
        return '-created'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['purpose'] = 'problem_all_submissions'
        context['problem'] = self.problem
        context['page_title'] = 'PNOJ: All Submissions for Problem ' + self.problem.name
        return context

class ProblemBestSubmissions(ListView):
    context_object_name = "submissions"
    template_name = 'judge/submission_list.html'
    paginate_by = 50

    def get_queryset(self):
        self.problem = get_object_or_404(models.Problem, slug=self.kwargs['slug'])
        return models.Submission.objects.filter(problem=self.problem).order_by(self.get_ordering())

    def get_ordering(self):
        return '-scored'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['purpose'] = 'problem_best_submissions'
        context['problem'] = self.problem
        context['page_title'] = 'PNOJ: Best Submissions for Problem ' + self.problem.name
        return context

class UserIndex(ListView):
    model = models.User
    context_object_name = 'users'
    template_name = 'judge/user_index.html'

    def get_ordering(self):
        return '-points'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['page_title'] = 'PNOJ: Users'
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
        context['page_title'] = 'PNOJ: User ' + self.get_object().username
        return context


class UserSubmissions(ListView):
    context_object_name = "submissions"
    template_name = 'judge/submission_list.html'
    paginate_by = 50

    def get_queryset(self):
        self.user = get_object_or_404(models.User, username=self.kwargs['slug'])
        return models.Submission.objects.filter(author=self.user).order_by(self.get_ordering())

    def get_ordering(self):
        return '-points'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['author'] = self.kwargs['slug']
        context['purpose'] = 'user_submissions'
        context['page_title'] = 'PNOJ: Submissions by User ' + self.user.username
        return context

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
        context['page_title'] = 'PNOJ: Update Profile'
        return context


class SubmissionIndex(ListView):
    model = models.Submission
    context_object_name = 'submissions'
    template_name = 'judge/submission_list.html'
    paginate_by = 50

    def get_ordering(self):
        return '-created'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['page_title'] = 'PNOJ: Submissions'
        return context



class Submission(DetailView):
    model = models.Submission
    context_object_name = 'submission'
    template_name = 'judge/submission.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sidebar_items'] = models.SidebarItem.objects.order_by('order')
        context['page_title'] = 'PNOJ: Submission #' + str(self.get_object().pk)
        return context

