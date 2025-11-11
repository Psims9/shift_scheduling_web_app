from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from .models import Worker
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import WorkerAvailabilityForm, MonthForm
import json
from .create_schedule import create_schedule

def index(request):
    num_workers = Worker.objects.all().count()
    context = {'num_workers': num_workers}
    return render(request, 'base_generic.html', context=context)

class WorkerListView(generic.ListView):
    model = Worker
    paginate_by = 10

class WorkerDetailView(generic.DetailView):
    model = Worker

class WorkerCreateView(CreateView):
    model = Worker
    fields = '__all__'

class WorkerUpdateView(UpdateView):
    model = Worker
    fields = ['first_name', 'last_name']

def edit_worker_availability(request, pk):

    worker = get_object_or_404(Worker, pk=pk)

    if request.method == 'POST':

        # When you create a ModelForm, it can be bound to an existing model instance.
        # If instance is not provided, the form will create a new object when saved.
        form = WorkerAvailabilityForm(request.POST, instance=worker)
        if form.is_valid():
            form.save()
            return redirect('workers')
        
    else:
        form = WorkerAvailabilityForm(instance=worker)
    
    initial_dates_json = json.dumps(worker.unavailable_dates or [])
    context = {
        'form': form,
        'worker': worker,
        'initial_dates_json': initial_dates_json
    }

    return render(request, 'edit-worker-availability.html', context=context)
            

class WorkerDeleteView(DeleteView):
    model = Worker
    success_url = reverse_lazy('workers')

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except:
            return HttpResponseRedirect('worker-delete', kwargs={'pk': self.object.pk})

def CreateSchedule(request):
    solution = None
    
    if request.method == 'POST':
        form = MonthForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['month']
            employees = Worker.objects.all().values()
            employee_data = [{'id': e['id'], 'avail': e['unavailable_dates']} for e in employees]
            solution = create_schedule(date, employee_data)
            id_to_name = {e['id']: f"{e['first_name']} {e['last_name']}" for e in employees}
            solution = {day: tuple(id_to_name[i] for i in ids_tuple) for day, ids_tuple in solution.items()}
    else:
        form = MonthForm()

    context = {
        'form': form,
        'solution': solution
    }
    
    return render(request, 'create-schedule.html', context=context)