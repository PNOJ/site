from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import pytz
import random
import pnoj.settings as settings


# Create your models here.

status_choices = [
    ('AC', 'Accepted'),
    ('WA', 'Wrong Answer'),
    ('TLE', 'Time Limit Exceeded'),
    ('MLE', 'Memory Limit Exceeded'),
    ('OLE', 'Output Limit Exceeded'),
    ('IR', 'Invalid Return'),
    ('IE', 'Internal Error'),
    ('AB', 'Aborted'),
]

class Programmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)

    timezone_choices = [(i, i) for i in pytz.common_timezones]
    timezone = models.CharField(max_length=50, choices=timezone_choices, default="UTC")

    main_language_choices = [(i['code'], i['name']) for i in settings.languages]
    main_language = models.CharField(max_length=10, choices=main_language_choices, default='py3')

    registered_date = models.DateTimeField(auto_now_add=True)

    organizations = models.ManyToManyField('Organization')


class Organization(models.Model):
    creator = models.ForeignKey(Programmer, on_delete=models.PROTECT, related_name="organizations_owning")
    admins = models.ManyToManyField('Programmer', related_name="organizations_maintaining")
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    
    is_private = models.BooleanField(default=False)

class Category(models.Model):
    name = models.CharField(max_length=12)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    class Meta:
        abstract = True

class ProblemCategory(Category):
    pass

class ProblemType(Category):
    pass

class Problem(models.Model):
    problem_file = models.FileField(upload_to="problems/")
    manifest_file = models.FileField()
    description_file = models.FileField()

    owner = models.ForeignKey(Programmer, on_delete=models.SET_NULL, null=True, blank=True, related_name="problems_owning")
    maintainers = models.ManyToManyField(Programmer, related_name="problems_maintaining")
    name = models.CharField(max_length=128)
    description = models.TextField()
    slug = models.SlugField(unique=True)

    points = models.PositiveSmallIntegerField()
    time_limit = models.FloatField()
    memory_limit = models.FloatField()

    category = models.ManyToManyField(ProblemCategory)
    problem_type = models.ManyToManyField(ProblemType)

class Submission(models.Model):
    author = models.ForeignKey(Programmer, on_delete=models.SET_NULL, null=True, blank=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)

    scored = models.PositiveSmallIntegerField()
    scoreable = models.PositiveSmallIntegerField()

    points = models.FloatField()

    time = models.FloatField()
    memory = models.FloatField()

    source = models.FileField(upload_to="submissions/")

    status = models.CharField(max_length=4, choices=status_choices)

class SubmissionBatchResult(models.Model):
    name = models.CharField(max_length=20)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)

    scored = models.PositiveSmallIntegerField()
    scoreable = models.PositiveSmallIntegerField()

    status = models.CharField(max_length=4, choices=status_choices)

    time = models.FloatField()
    memory = models.FloatField()

class SubmissionTestcaseResult(models.Model):
    name = models.CharField(max_length=20)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    batch = models.ForeignKey(SubmissionBatchResult, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)

    status = models.CharField(max_length=4, choices=status_choices)

    time = models.FloatField()
    memory = models.FloatField()

class Comment(models.Model):
    parent_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    parent_object_id = models.PositiveIntegerField()
    parent = GenericForeignKey('parent_content_type', 'parent_object_id')

    author = models.ForeignKey(Programmer, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    text = models.TextField()
