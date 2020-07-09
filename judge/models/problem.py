from django.db import models
import uuid
import zipfile
import yaml
from .profile import User

# Create your models here.

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

