from django.views.generic import DetailView, ListView
from .. import models
from django.views.generic.base import RedirectView
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from . import mixin

class SubmissionIndex(ListView, mixin.TitleMixin):
    model = models.Submission
    context_object_name = 'submissions'
    template_name = 'judge/submission/list.html'
    paginate_by = 50
    title = 'PNOJ: Submissions'

    def get_ordering(self):
        return '-created' 

class Submission(DetailView, mixin.TitleMixin):
    model = models.Submission
    context_object_name = 'submission'
    template_name = 'judge/submission/detail.html'

    def get_title(self):
        return 'PNOJ: Submission #' + str(self.get_object().pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission_contenttype = ContentType.objects.get_for_model(models.Submission)
        context['comments'] = models.Comment.objects.filter(parent_content_type=submission_contenttype, parent_object_id=self.get_object().pk)
        context['source_viewable'] = self.get_object().author == self.request.user or (self.request.user.is_authenticated and self.request.user.has_solved(self.get_object().problem))
        return context

class SubmissionSource(UserPassesTestMixin, DetailView, mixin.TitleMixin):
    model = models.Submission
    context_object_name = 'submission'
    template_name = 'judge/submission/source.html'

    def test_func(self):
        return self.get_object().author == self.request.user or (self.request.user.is_authenticated and self.request.user.has_solved(self.get_object().problem))

    def get_title(self):
        return 'PNOJ: Submission #' + str(self.get_object().pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission_contenttype = ContentType.objects.get_for_model(models.Submission)
        with self.get_object().source.open() as sourcefile:
            context['source'] = sourcefile.read().decode('ascii').strip()
        return context

def get_submission_data(request, pk):
    submission_data = cache.get(f'passthrough-{pk}')
    submission = models.Submission.objects.get(pk=pk)

    if submission_data == None:
        submission_data = dict()

        submission_data["type"] = "result"
        submission_data["score"] = dict()
        submission_data["score"]["scored"] = submission.scored
        submission_data["score"]["scoreable"] = submission.scoreable
        submission_data["score"]["points"] = submission.points
        submission_data["score"]["max_points"] = submission.problem.points
        submission_data["status"] = submission.status
        if submission.message != "":
            submission_data["message"] = submission.message
        submission_data["resource"] = dict()
        submission_data["resource"]["time"] = submission.time
        submission_data["resource"]["memory"] = submission.memory
        submission_data["batches"] = list()

        for batch in submission.submissionbatchresult_set.all():
            batch_data = dict()
            batch_data["name"] = batch.name
            batch_data["type"] = "batch"
            batch_data["status"] = batch.status
            if batch.message != "":
                batch_data["message"] = batch.message
            batch_data["resource"] = dict()
            batch_data["resource"]["time"] = batch.time
            batch_data["resource"]["memory"] = batch.memory
            batch_data["score"] = dict()
            batch_data["score"]["scored"] = batch.scored
            batch_data["score"]["scoreable"] = batch.scoreable
            batch_data["testcases"] = list()

            for testcase in batch.submissiontestcaseresult_set.all():
                testcase_data = dict()
                testcase_data["name"] = testcase.name
                testcase_data["type"] = "testcase"
                testcase_data["resource"] = dict()
                testcase_data["resource"]["time"] = testcase.time
                testcase_data["resource"]["memory"] = testcase.memory
                testcase_data["status"] = testcase.status
                if testcase.message != "":
                    testcase_data["message"] = testcase.message

                batch_data["testcases"].append(testcase_data)

            submission_data["batches"].append(batch_data)
        submission_data["language"] = dict()
        submission_data["language"]["code"] = submission.language
        submission_data["language"]["display"] = submission.get_language_display()
    else:
        language_data = cache.get(f"language-{submission.pk}")
        submission_data["language"] = dict()
        submission_data["language"]["code"] = language_data[0]
        submission_data["language"]["display"] = language_data[1]
    
    return JsonResponse(dict(submission_data))
