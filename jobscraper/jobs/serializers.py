# jobs/serializers.py
from rest_framework import serializers
from .models import Job, ScrapeLog

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

class ScrapeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapeLog
        fields = '__all__'

class ScrapeTriggerSerializer(serializers.Serializer):
    source = serializers.ChoiceField(choices=['indeed', 'linkedin', 'glassdoor'])
    search_query = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255, required=False, allow_blank=True)
    max_pages = serializers.IntegerField(min_value=1, max_value=5, default=1)