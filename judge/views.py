from django.shortcuts import render, redirect
from .models import Problems
# Create your views here.

def index(request):
    return redirect('/problems/')

def problems(request):
    problems = Problems.objects.all()
    args = {'problems': problems}
    return render(request, 'judge/problems.html', args)
