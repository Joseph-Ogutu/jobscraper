# jobs/views.py
import threading
from django.shortcuts import render
from django.utils import timezone
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job, ScrapeLog
from .serializers import JobSerializer, ScrapeLogSerializer, ScrapeTriggerSerializer
from .scraper import scrape_jobs_from_source

class JobListView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source', 'company', 'is_active']
    search_fields = ['title', 'company', 'description', 'location']
    ordering_fields = '__all__'
    ordering = ['-scraped_at']

class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

class ScrapeLogListView(generics.ListAPIView):
    queryset = ScrapeLog.objects.all()
    serializer_class = ScrapeLogSerializer

class ScrapeLogDetailView(generics.RetrieveAPIView):
    queryset = ScrapeLog.objects.all()
    serializer_class = ScrapeLogSerializer

class JobStatsView(APIView):
    def get(self, request):
        total_jobs = Job.objects.count()
        active_jobs = Job.objects.filter(is_active=True).count()
        top_companies = list(Job.objects.values_list('company', flat=True).distinct())
        by_source = list(Job.objects.values('source').distinct())
        return Response({
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'top_companies': top_companies,
            'by_source': by_source,
        })

class ScrapeJobsView(APIView):
    def post(self, request):
        serializer = ScrapeTriggerSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Start scraping in background thread
            def run_scrape():
                scrape_jobs_from_source(
                    source=data['source'],
                    query=data['search_query'],
                    location=data.get('location', ''),
                    max_pages=data['max_pages']
                )
            
            thread = threading.Thread(target=run_scrape)
            thread.start()
            
            return Response(
                {"message": "Scraping started in background", "data": data},
                status=status.HTTP_202_ACCEPTED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DashboardView(APIView):
    def get(self, request):
        return render(request, 'dashboard.html')