from django.views.generic import DetailView, ListView
from .. import models
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import uuid
from django.core.cache import cache
from django.urls import reverse
from pnoj import settings
import logging
import json
import requests
from dyndict import dyndict
from . import mixin

logger = logging.getLogger('django')

class ProblemList(ListView, mixin.TitleMixin, mixin.MetaMixin):
    model = models.Problem
    context_object_name = 'problems'
    template_name = 'judge/problem/list.html'
    title = 'PNOJ: Problems'

    def get_ordering(self):
        return 'name'

class ProblemDetail(DetailView, mixin.TitleMixin, mixin.MetaMixin):
    model = models.Problem
    context_object_name = 'problem'
    template_name = "judge/problem/detail.html"

    def get_title(self):
        return 'PNOJ: ' + self.get_object().name

    def get_description(self):
        return self.get_object().description

    def get_author(self):
        return self.get_object().author.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        problem_contenttype = ContentType.objects.get_for_model(models.Problem)
        context['comments'] = models.Comment.objects.filter(parent_content_type=problem_contenttype, parent_object_id=self.get_object().pk)
        return context

def create_judge_task(submission_id, problem_file_url, submission_file_url, language, callback_url, passthrough_url):
    post_data = {
        'problem_file_url': problem_file_url,
        'submission_file_url': submission_file_url,
        'language': language,
        'callback_url': callback_url,
        'passthrough_url': passthrough_url,
        'token': settings.judge['token'],
    }
    response = requests.post(f"{settings.judge['endpoint']}/create/task", data=post_data)
    response.raise_for_status()

@method_decorator(login_required, name='dispatch')
class ProblemSubmit(CreateView, mixin.TitleMixin, mixin.MetaMixin):
    template_name = 'judge/problem/submit.html'
    model = models.Submission
    fields = ('source', 'language')

    def form_valid(self, form, **kwargs):
        model = form.save(commit=False)
        model.author = self.request.user
        model.problem = models.Problem.objects.get(slug=self.kwargs['slug'])
        model.status = 'MD'
        model.save()

        callback_uuid = uuid.uuid4().hex
        cache.set('callback-{0}'.format(callback_uuid), model.pk, 1800)
        cache.set('passthrough-{0}'.format(model.pk), dyndict(refer_by="name"), 1800)
        cache.set('language-{0}'.format(model.pk), (model.language, model.get_language_display()), 1800)
        callback_url = self.request.build_absolute_uri(reverse('callback', kwargs={'uuid': callback_uuid}))
        passthrough_url = self.request.build_absolute_uri(reverse('passthrough', kwargs={'uuid': callback_uuid}))
        submission_file_url = self.request.build_absolute_uri(model.source.url)
        problem_file_url = self.request.build_absolute_uri(model.problem.problem_file.url)
        if hasattr(settings, 'override_callback_url'):
            logger.info("Callback url for submission #{0}: {1}".format(model.pk, callback_url))
            callback_url = settings.override_callback_url.format(callback_uuid)
        if hasattr(settings, 'override_passthrough_url'):
            logger.info("Passthrough url for submission #{0}: {1}".format(model.pk, passthrough_url))
            passthrough_url = settings.override_passthrough_url.format(callback_uuid)
        if hasattr(settings, 'override_submission_file_url'):
            logger.info("Submission file url for submission #{0}: {1}".format(model.pk, submission_file_url))
            submission_file_url = settings.override_submission_file_url.format(model.problem.slug, model.language)
        if hasattr(settings, 'override_problem_file_url'):
            logger.info("Problem file url for submission #{0}: {1}".format(model.pk, problem_file_url))
            problem_file_url = settings.override_problem_file_url.format(model.problem.slug)
        create_judge_task(model.pk, problem_file_url, submission_file_url, model.language, callback_url, passthrough_url)

        return super().form_valid(form)

    def get_object(self):
        return models.Problem.objects.get(slug=self.kwargs['slug'])

    def get_title(self):
        return 'PNOJ: Submit to ' + self.get_object().name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.get_object()
        return context

@csrf_exempt
@require_POST
def callback(request, uuid):
    submission_pk = cache.get("callback-{0}".format(uuid))

    result = json.loads(request.body)

    logger.info(result)

    submission = models.Submission.objects.get(pk=submission_pk)
    if 'score' in result and result['score']['scoreable'] != None:
        submission.scored = result['score']['scored']
        submission.scoreable = result['score']['scoreable']
        submission.points = (result['score']['scored']/result['score']['scoreable'])*submission.problem.points
    else:
        submission.points = 0
    submission.status = result['status']
    if 'resource' in result:
        submission.time = result['resource']['time']
        submission.memory = result['resource']['memory']
    if 'message' in result and not result['message'] == None:
        submission.message = result['message']

    submission.save()

    for batch_result in result['batches']:
        batch = models.SubmissionBatchResult()
        batch.name = batch_result['name']
        batch.submission = submission
        if 'message' in batch_result and not batch_result['message'] == None:
            batch.message = batch_result['message']
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
            if 'message' in testcase_result and not testcase_result['message'] == None:
                testcase.message = testcase_result['message']
            testcase.status = testcase_result['status']
            if 'resource' in testcase_result:
                testcase.time = testcase_result['resource']['time']
                testcase.memory = testcase_result['resource']['memory']
            testcase.save()

    submission.author.save()

    cache.delete("passthrough-{0}".format(submission.pk))

    return HttpResponse("OK")

@csrf_exempt
@require_POST
def passthrough(request, uuid):
    submission_pk = cache.get(f"callback-{uuid}")
    previous_status = cache.get(f"passthrough-{submission_pk}")

    result = json.loads(request.body)

    previous_status += result

    cache.set(f"passthrough-{submission_pk}", previous_status, 1800)

    logger.info(result)

    return HttpResponse("OK")


class ProblemAllSubmissions(ListView, mixin.TitleMixin, mixin.MetaMixin):
    context_object_name = "submissions"
    template_name = 'judge/problem/all_submission.html'
    paginate_by = 50

    def get_queryset(self):
        self.problem = get_object_or_404(models.Problem, slug=self.kwargs['slug'])
        return models.Submission.objects.filter(problem=self.problem).order_by(self.get_ordering())

    def get_ordering(self):
        return '-created'

    def get_title(self):
        return 'PNOJ: All Submissions for Problem ' + self.problem.name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.problem
        return context

class ProblemBestSubmissions(ListView, mixin.TitleMixin, mixin.MetaMixin):
    context_object_name = "submissions"
    template_name = 'judge/problem/best_submission.html'
    paginate_by = 50

    def get_queryset(self):
        self.problem = get_object_or_404(models.Problem, slug=self.kwargs['slug'])
        return models.Submission.objects.filter(problem=self.problem).order_by(self.get_ordering())

    def get_ordering(self):
        return '-points'

    def get_title(self):
        return 'PNOJ: Best Submissions for Problem ' + self.problem.name

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['problem'] = self.problem
        return context
