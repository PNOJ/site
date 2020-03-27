from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import pytz
import random
import pnoj.settings as settings
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum
import uuid
import zipfile
import yaml
from django.utils import timezone
import datetime

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
    ('G', 'Grading'),
    ('MD', 'Missing Data'),
]

language_choices = [(i['code'], i['name']) for i in settings.languages.values()]


class User(AbstractUser):
    email = models.EmailField(unique=True)
    description = models.TextField(blank=True)

    timezone_choices = [(i, i) for i in pytz.common_timezones]
    timezone = models.CharField(max_length=50, choices=timezone_choices, default="UTC")

    main_language = models.CharField(max_length=10, choices=language_choices, default='py3')

    registered_date = models.DateTimeField(auto_now_add=True)

    organizations = models.ManyToManyField('Organization', blank=True)

    points = models.FloatField(default=0)
    num_problems_solved = models.PositiveIntegerField(default=0)

    def has_attempted(self, problem):
        queryset = Submission.objects.filter(author=self).filter(problem=problem)
        return bool(queryset)

    def has_solved(self, problem):
        submissions = Submission.objects.filter(author=self).filter(problem=problem)
        for i in submissions:
            if i.scoreable == None:
                continue
            if i.scored == i.scoreable:
                return True
        return False

    def calculate_points(self):
        submissions = self.submission_set.all()
        points = {}
        for i in submissions:
            if not i.points:
                continue
            elif i.problem.pk in points:
                points[i.problem.pk] = max(points[i.problem.pk], i.points)
            else:
                points[i.problem.pk] = i.points
        return sum(points.values())

    def calculate_num_problems_solved(self):
        solved_problems = set()
        submissions = self.submission_set.all()
        for i in submissions:
            if i.scored == i.scoreable and i.problem.name not in solved_problems:
                solved_problems.add(i.problem.name)
        return len(solved_problems)

    def update_stats(self):
        self.points = self.calculate_points()
        self.num_problems_solved = self.calculate_num_problems_solved()

    def save(self, *args, **kwargs):
        self.update_stats()
        super().save(*args, **kwargs)


class Organization(models.Model):
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name="organizations_owning")
    admins = models.ManyToManyField('User', related_name="organizations_maintaining")
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    
    is_private = models.BooleanField(default=False)

class Category(models.Model):
    name = models.CharField(max_length=30)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class ProblemCategory(Category):
    pass

class ProblemType(Category):
    pass

def problem_file_path(instance, filename):
    ext = filename.split(".")[-1]
    uuid_hex = uuid.uuid4().hex
    return "problems/{0}.{1}".format(uuid_hex, ext)

class Problem(models.Model):
    problem_file = models.FileField(upload_to=problem_file_path, unique=True)
    manifest = models.TextField()

    author = models.ManyToManyField(User, related_name="problems_authored", blank=True)
    name = models.CharField(max_length=128)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    created = models.DateTimeField(auto_now_add=True)

    points = models.PositiveSmallIntegerField()
    is_partial = models.BooleanField()
    time_limit = models.FloatField()
    memory_limit = models.FloatField()

    category = models.ManyToManyField(ProblemCategory, blank=True)
    problem_type = models.ManyToManyField(ProblemType, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        with zipfile.ZipFile(self.problem_file.file) as z:
            with z.open('manifest.yaml') as manifest_file:
                self.manifest = manifest_file.read()
            manifest_dict = yaml.safe_load(self.manifest)        

            self.name = manifest_dict['name']

            with z.open(manifest_dict['metadata']['description'], "r") as description_file:
                self.description = description_file.read().decode("utf-8").strip("\n")

            self.points = manifest_dict['metadata']['points']
            self.is_partial = manifest_dict['metadata']['partial']

            self.time_limit = manifest_dict['metadata']['limit']['time']
            self.memory_limit = manifest_dict['metadata']['limit']['memory']
            
        super().save(*args, **kwargs)  # Call the "real" save() method.

        authors = User.objects.filter(username__in=manifest_dict['author'])
        self.author.set(authors)

        categories = ProblemCategory.objects.filter(name__in=manifest_dict['metadata']['category'])
        self.category.set(list(categories))
        problem_types = ProblemType.objects.filter(name__in=manifest_dict['metadata']['type'])
        self.problem_type.set(problem_types)

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

class Comment(models.Model):
    parent_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    parent_object_id = models.PositiveIntegerField()
    parent = GenericForeignKey('parent_content_type', 'parent_object_id')

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    text = models.TextField()

class SidebarItem(models.Model):
    name = models.CharField(max_length=24)
    view = models.CharField(max_length=64)
    order = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    author = models.ManyToManyField(User, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=128, blank=True)
    text = models.TextField(blank=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title

