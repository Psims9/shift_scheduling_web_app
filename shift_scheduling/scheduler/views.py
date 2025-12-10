from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from .models import Worker, Schedule
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .forms import WorkerDataForm, MonthForm
import json
from .create_schedule import create_schedule
from .data_checks import data_checks
import csv
from django.views.decorators.http import require_POST

@login_required
def index(request):
    num_workers = Worker.objects.all().count()
    context = {'num_workers': num_workers}
    return render(request, 'base_generic.html', context=context)

class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = Worker
    

class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker

class WorkerCreateView(LoginRequiredMixin, CreateView):
    model = Worker
    fields = ['first_name', 'last_name']
    success_url = reverse_lazy('workers')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Add classes to fields
        for field_name in form.fields:
            form.fields[field_name].widget.attrs.update({'class': 'form-input-field'})
        return form

class WorkerUpdateView(LoginRequiredMixin, UpdateView):
    model = Worker
    fields = ['first_name', 'last_name']

@login_required
def worker_data(request, pk):

    worker = get_object_or_404(Worker, pk=pk)

    if request.method == 'POST':

        # When you create a ModelForm, it can be bound to an existing model instance.
        # If instance is not provided, the form will create a new object when saved.

        form = WorkerDataForm(request.POST, instance=worker)
        if form.is_valid():
            form.save()
            return redirect('workers')
        
    else:
        form = WorkerDataForm(instance=worker)
    
    initial_dates_json = json.dumps(worker.unavailable_dates or [])
    context = {
        'form': form,
        'worker': worker,
        'initial_dates_json': initial_dates_json
    }

    return render(request, 'worker_data.html', context=context)
            

class WorkerDeleteView(LoginRequiredMixin, DeleteView):
    model = Worker
    success_url = reverse_lazy('workers')

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except:
            return HttpResponseRedirect('worker_delete', kwargs={'pk': self.object.pk})

@login_required
def CreateSchedule(request):
    data_error_msg = ''
    solver = 'successful'
    

    if request.method == 'POST':
        # if it is a post request, first run some first-line checks on the DB
        # for obvious things and edge cases which might cause create_schedule to fail,
        # such as not enough workers, too many constraints etc.

        form = MonthForm(request.POST)

        if form.is_valid():

            employees = Worker.objects.all()
            schedule_period = form.cleaned_data['schedule_period']

            test_results = data_checks(employees, schedule_period)

            if test_results['code'] == 0:

                result = create_schedule(schedule_period, employees)

                if result == None:
                    solver = 'unsuccessful'
                    
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
                data_error_msg = test_results['msg']
            
    else:
        form = MonthForm()

    context = {
        'form': form,
        'solver': solver,
        'data_error_msg': data_error_msg
    }
    
    return render(request, 'create_schedule.html', context=context)

@login_required
def DisplaySchedule(request, pk):
    schedule = Schedule.objects.get(pk=pk)
    return render(request, 'display_schedule.html', context={'schedule': schedule})

class ScheduleListView(LoginRequiredMixin, generic.ListView):
    model = Schedule
    paginate_by: 10

class ScheduleDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Schedule
    success_url = reverse_lazy('schedules')

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except:
            return HttpResponseRedirect('schedule_delete', kwargs={'pk': self.object.pk})
        

@login_required
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

@login_required
def worker_bulk_action_confirm(request):
    # Recieves POST requests with data from forms submitted in the list pages (schedules or employees)
    # These forms include checkboxes with values equal to worker IDs as well as a the value
    # of the <select name="action"> element (delete or reset_data)
    # Based these IDs and the action type, we want query these  instances
    # and render a "confirm_bulk_action.html" tempalte which contains a list
    # of the selected instances and the action to be performed, asking for confirmation
    # before calling the view which performs the action

    # get data from the POST request
    selected_ids = request.POST.getlist('selected')
    action = request.POST.get('action')

    # query the DB
    workers = Worker.objects.filter(id__in=selected_ids)

    # populate context var
    context = {
        'selected_ids': selected_ids,
        'action': action,        
        'workers': workers,
    }

    return render(request, 'worker_bulk_confirm.html', context)

@require_POST
@login_required
def worker_bulk_action(request):
    selected_ids = request.POST.getlist('selected')
    action = request.POST.get('action')
    workers = Worker.objects.filter(id__in=selected_ids)

    if action == 'delete':
        workers.delete()
    
    elif action == 'reset':
        workers.update(
            unavailable_dates=[],
            assign_least_shifts=False,
            assign_least_weekends=False
        )
    
    return redirect('workers')