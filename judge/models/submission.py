from django.db import models
import uuid
from django.utils import timezone
import datetime
from .choices import status_choices, language_choices
from .profile import User
from .problem import Problem

# Create your models here.

def submission_file_path(instance, filename):
    ext = filename.split(".")[-1]
    uuid_hex = uuid.uuid4().hex
    return "submissions/{0}.{1}".format(uuid_hex, ext)

class Submission(models.Model):
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)

    scored = models.PositiveSmallIntegerField(null=True, blank=True)
    scoreable = models.PositiveSmallIntegerField(null=True, blank=True)

    points = models.FloatField(null=True, blank=True, default=0)

    time = models.FloatField(null=True, blank=True)
    memory = models.FloatField(null=True, blank=True)

    source = models.FileField(upload_to=submission_file_path)

    status = models.CharField(max_length=4, choices=status_choices, blank=True)

    language = models.CharField(max_length=10, choices=language_choices, null=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('submission', args=[self.pk])

    @property
    def status_display(self):
        if self.status == 'MD':
            if timezone.now() - self.created <= datetime.timedelta(minutes=30):
                return 'G'
            else:
                return 'IE'
        else:
            return self.status

class SubmissionBatchResult(models.Model):
    name = models.CharField(max_length=20)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)

    scored = models.PositiveSmallIntegerField()
    scoreable = models.PositiveSmallIntegerField()

    status = models.CharField(max_length=4, choices=status_choices)

    time = models.FloatField(null=True, blank=True)
    memory = models.FloatField(null=True, blank=True)

class SubmissionTestcaseResult(models.Model):
    name = models.CharField(max_length=20)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    batch = models.ForeignKey(SubmissionBatchResult, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)

    status = models.CharField(max_length=4, choices=status_choices)

    time = models.FloatField(null=True, blank=True)
    memory = models.FloatField(null=True, blank=True)

