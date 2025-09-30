from django.db import models
from django.utils import timezone

class Job(models.Model):
    """Model to store scraped job listings"""
    
    # Job Details
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    salary = models.CharField(max_length=100, blank=True, null=True)
    job_type = models.CharField(max_length=50, blank=True, null=True)  # Full-time, Part-time, etc.
    
    # Description
    description = models.TextField(blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    
    # Meta Information
    source = models.CharField(max_length=50)  # LinkedIn, Indeed, Glassdoor
    source_url = models.URLField(max_length=500, unique=True)  # Prevent duplicates!
    posted_date = models.DateField(blank=True, null=True)
    
    # Tracking
    scraped_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-scraped_at']
        indexes = [
            models.Index(fields=['company', 'title']),
            models.Index(fields=['source']),
        ]
    
    def __str__(self):
        return f"{self.title} at {self.company}"


class ScrapeLog(models.Model):
    """Track scraping activities and errors"""
    
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('partial', 'Partial'),
    ]
    
    source = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    jobs_scraped = models.IntegerField(default=0)
    duplicates_found = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.source} - {self.status} ({self.jobs_scraped} jobs)"