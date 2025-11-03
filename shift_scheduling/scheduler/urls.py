from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('workers/', views.WorkerListView.as_view(), name='workers'),
    path('worker/<int:pk>', views.WorkerDetailView.as_view(), name='detail-worker'),    
]