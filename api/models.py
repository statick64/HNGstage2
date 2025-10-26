from django.db import models
from django.utils import timezone


class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    capital = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    population = models.BigIntegerField()
    currency_code = models.CharField(max_length=10, null=True)
    exchange_rate = models.FloatField(null=True)
    estimated_gdp = models.FloatField(null=True)
    flag_url = models.URLField(max_length=500, null=True, blank=True)
    last_refreshed_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name


class RefreshStatus(models.Model):
    total_countries = models.IntegerField(default=0)
    last_refreshed_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Refresh at {self.last_refreshed_at}"
