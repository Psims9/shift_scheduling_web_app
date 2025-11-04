from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Worker
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

def index(request):
    num_workers = Worker.objects.all().count()
    context = {'num_workers': num_workers}
    return render(request, 'base_generic.html', context=context)

class WorkerListView(generic.ListView):
    model = Worker
    paginate_by = 10

class WorkerDetailView(generic.DetailView):
    model = Worker

class WorkerCreate(CreateView):
    model = Worker
    fields = '__all__'

class WorkerUpdate(UpdateView):
    model = Worker
    fields = '__all__'

class WorkerDelete(DeleteView):
    model = Worker
    success_url = reverse_lazy('workers')

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except:
            return HttpResponseRedirect('worker-delete', kwargs={'pk': self.object.pk})
