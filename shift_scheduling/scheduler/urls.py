from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateSchedule, name='create_schedule'),
    path('schedule/<int:pk>', views.DisplaySchedule, name='display_schedule'),
    path('schedule/<int:pk>/delete/', views.ScheduleDeleteView.as_view(), name='schedule_delete'),
    path('schedules/', views.ScheduleListView.as_view(), name='schedules'),
    
    path('worker/create/', views.WorkerCreateView.as_view(), name='worker_create'),
    path('worker/<int:pk>/', views.worker_data, name='worker_data'),
    path('worker/<int:pk>/delete/', views.WorkerDeleteView.as_view(), name='worker_delete'),
    path('workers/', views.WorkerListView.as_view(), name='workers'),

    path('schedule/<int:pk>/download_csv', views.download_schedule_csv, name="download_schedule_csv")
]
