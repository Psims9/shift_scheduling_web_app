from django.shortcuts import render
from .models import Worker
from django.views import generic

def index(request):
    num_workers = Worker.objects.all().count()
    context = {'num_workers': num_workers}
    return render(request, 'base_generic.html', context=context)

class WorkerListView(generic.ListView):
    model = Worker

class WorkerDetailView(generic.DetailView):
    model = Worker