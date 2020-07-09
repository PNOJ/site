from django.db import models
from .choices import language_choices, timezone_choices
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    description = models.TextField(blank=True)

    timezone = models.CharField(max_length=50, choices=timezone_choices, default="UTC")

    main_language = models.CharField(max_length=10, choices=language_choices, default='python3')

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
