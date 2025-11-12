from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateSchedule, name='create_schedule'),
    path('workers/', views.WorkerListView.as_view(), name='workers'),
    path('worker/<int:pk>', views.WorkerDetailView.as_view(), name='detail_worker'),
    path('worker/create/', views.WorkerCreateView.as_view(), name='worker_create'),
    path('worker/<int:pk>/update/', views.WorkerUpdateView.as_view(), name='worker_update'),
    path('worker/<int:pk>/delete/', views.WorkerDeleteView.as_view(), name='worker_delete'),
    path('worker/<int:pk>/availability', views.edit_worker_availability, name='edit_worker_availability'),
    path('schedule/<int:pk>', views.DisplaySchedule, name='display_schedule'),
]