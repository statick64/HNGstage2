from rest_framework import serializers
from .models import Country, RefreshStatus


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            'id', 'name', 'capital', 'region', 'population',
            'currency_code', 'exchange_rate', 'estimated_gdp',
            'flag_url', 'last_refreshed_at'
        ]
        read_only_fields = ['id', 'last_refreshed_at']


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefreshStatus
        fields = ['total_countries', 'last_refreshed_at']
