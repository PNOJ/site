from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class Problem(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    title = models.CharField(max_length=75)
    partial_point = models.BooleanField(default=False)
    memory_limit = models.FloatField()
    time_limit = models.FloatField()
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = models.DateTimeField(auto_now=True)

class Testcase(models.Model):
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    problem = models.ForeignKey(Problem, on_delete=models.PROTECT)
    created_date = models.DateTimeField(auto_now_add=True)
    last_modified_date = mode.DateTimeField(auto_now=True)
    id = models.CharField(max_length=10)
    points = models.PositiveSmallIntegerField()
    testcase_input = models.TextField()
    testcase_output = models.TextField()

class Submission(models.Model):
    created_date = model.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    problem = models.ForeignKey(Problem, on_delete=models.PROTECT)
    valid = models.BooleanField(default=True)

class TestcaseResult(models.Model):
    status_codes = [
        ('AC', 'Accepted'),
        ('WA', 'Wrong Answer'),
        ('IR', 'Invalid Return'),
        ('RTE', 'Runtime Exception'),
        ('TLE', 'Time Limit Exceeded'),
        ('IE', 'Internal Error')
    ]
    execution_duration = models.FloatField()
    memory_used = models.FloatField()
    status = models.CharField(
        max_length=5,
        choices=status_codes,
    )
    submission = models.ForeignKey(Submission, on_delete.models.PROTECT)

class User(AbstractUser):
    pass
