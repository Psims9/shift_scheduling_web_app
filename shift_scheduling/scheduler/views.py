from django.shortcuts import render
from .models import Worker

def index(request):
    num_workers = Worker.objects.all().count()
    context = {'num_workers': num_workers}
    return render(request, 'index.html', context=context)