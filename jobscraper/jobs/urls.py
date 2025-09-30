# jobs/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/jobs/', views.JobListView.as_view(), name='job-list'),
    path('api/jobs/<int:pk>/', views.JobDetailView.as_view(), name='job-detail'),
    path('api/jobs/scrape/', views.ScrapeJobsView.as_view(), name='scrape-jobs'),
    path('api/jobs/stats/', views.JobStatsView.as_view(), name='job-stats'),
    
    path('api/logs/', views.ScrapeLogListView.as_view(), name='log-list'),
    path('api/logs/<int:pk>/', views.ScrapeLogDetailView.as_view(), name='log-detail'),
    
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]