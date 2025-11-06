from django.urls import path
from . import views

urlpatterns = [
    path('', views.CreateSchedule, name='create-schedule'),
    path('workers/', views.WorkerListView.as_view(), name='workers'),
    path('worker/<int:pk>', views.WorkerDetailView.as_view(), name='detail-worker'),
    path('worker/create/', views.WorkerCreateView.as_view(), name='worker-create'),
    path('worker/<int:pk>/update/', views.WorkerUpdateView.as_view(), name='worker-update'),
    path('worker/<int:pk>/delete/', views.WorkerDeleteView.as_view(), name='worker-delete'),
    path('worker/<int:pk>/availability', views.edit_worker_availability, name='edit-worker-availability'),
]