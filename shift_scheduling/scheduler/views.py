from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse, Http404
from .models import Worker, Schedule
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import WorkerAvailabilityForm, MonthForm
import json
from .create_schedule import create_schedule
import csv

def index(request):
    num_workers = Worker.objects.all().count()
    context = {'num_workers': num_workers}
    return render(request, 'base_generic.html', context=context)

class WorkerListView(generic.ListView):
    model = Worker
    

class WorkerDetailView(generic.DetailView):
    model = Worker

class WorkerCreateView(CreateView):
    model = Worker
    fields = ['first_name', 'last_name']

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

    return render(request, 'edit_worker_availability.html', context=context)
            

class WorkerDeleteView(DeleteView):
    model = Worker
    success_url = reverse_lazy('workers')

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except:
            return HttpResponseRedirect('worker_delete', kwargs={'pk': self.object.pk})

def CreateSchedule(request):
    success = True
    
    if request.method == 'POST':
        form = MonthForm(request.POST)
        if form.is_valid():
            schedule_period = form.cleaned_data['schedule_period']
            employees = Worker.objects.all()

            result = create_schedule(schedule_period, employees)

            if result == None:
                success = False
                
            else:
                per_day_schedule, per_employee_schedule, schedule_stats = result
                new_schedule = Schedule.objects.create(
                    schedule_period=schedule_period,
                    per_day_schedule=per_day_schedule,
                    per_employee_schedule=per_employee_schedule,
                    schedule_stats = schedule_stats,
                )
                return redirect('display_schedule', pk=new_schedule.pk)

    else:
        form = MonthForm()

    context = {
        'form': form,
        'success': success
    }
    
    return render(request, 'create_schedule.html', context=context)

def DisplaySchedule(request, pk):
    schedule = Schedule.objects.get(pk=pk)
    return render(request, 'display_schedule.html', context={'schedule': schedule})

class ScheduleListView(generic.ListView):
    model = Schedule
    paginate_by: 10

class ScheduleDeleteView(generic.DeleteView):
    model = Schedule
    success_url = reverse_lazy('schedules')

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except:
            return HttpResponseRedirect('schedule_delete', kwargs={'pk': self.object.pk})
        

def download_schedule_csv(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    per_day = schedule.per_day_schedule # list of dictionaries

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    filename = f"schedule_{schedule.schedule_period.strftime('%Y-%m')}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')

    writer.writerow(['date', 'id', 'name'])
    
    for day in per_day:
        date = day.get('iso_date', '')
        employees = day.get('daily_employees', []) or [] # list of dictionaries

        for employee in employees:
            employee_name = employee.get('name','')
            employee_id = employee.get('id','')

            writer.writerow([date, employee_id, employee_name])
    
    return response
            