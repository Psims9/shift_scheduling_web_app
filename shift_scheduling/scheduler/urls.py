from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('workers/', views.WorkerListView.as_view(), name='workers'),
    path('worker/<int:pk>', views.WorkerDetailView.as_view(), name='detail-worker'),
    path('worker/create/', views.WorkerCreate.as_view(), name='worker-create'),
    path('worker/<int:pk>/update/', views.WorkerUpdate.as_view(), name='worker-update'),
    path('worker/<int:pk>/delete/', views.WorkerDelete.as_view(), name='worker-delete'),    
]