import os
import random
import requests
import datetime
from django.http import JsonResponse, HttpResponse, FileResponse
from django.utils import timezone
from django.conf import settings
from django.db.models import F
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Country, RefreshStatus
from .serializers import CountrySerializer, StatusSerializer
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


class CountryListView(APIView):
    def get(self, request):
        queryset = Country.objects.all()
        
        # Apply filters if provided
        region = request.query_params.get('region')
        currency = request.query_params.get('currency')
        sort = request.query_params.get('sort')
        
        if region:
            queryset = queryset.filter(region__iexact=region)
            
        if currency:
            queryset = queryset.filter(currency_code__iexact=currency)
        
        # Apply sorting
        if sort == 'gdp_desc':
            queryset = queryset.order_by('-estimated_gdp')
        elif sort == 'gdp_asc':
            queryset = queryset.order_by('estimated_gdp')
        
        serializer = CountrySerializer(queryset, many=True)
        return Response(serializer.data)


class CountryDetailView(APIView):
    def get(self, request, name):
        try:
            country = Country.objects.get(name__iexact=name)
            serializer = CountrySerializer(country)
            return Response(serializer.data)
        except Country.DoesNotExist:
            return Response({'error': 'Country not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, name):
        try:
            country = Country.objects.get(name__iexact=name)
            country.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Country.DoesNotExist:
            return Response({'error': 'Country not found'}, status=status.HTTP_404_NOT_FOUND)


class StatusView(APIView):
    def get(self, request):
        try:
            refresh_status = RefreshStatus.objects.latest('last_refreshed_at')
            serializer = StatusSerializer(refresh_status)
            return Response(serializer.data)
        except RefreshStatus.DoesNotExist:
            return Response({
                'total_countries': 0,
                'last_refreshed_at': None
            })


class RefreshCountriesView(APIView):
    def post(self, request):
        try:
            # Fetch countries
            countries_response = requests.get(
                'https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies',
                timeout=10
            )
            countries_data = countries_response.json()
            
            # Fetch exchange rates
            exchange_response = requests.get('https://open.er-api.com/v6/latest/USD', timeout=10)
            exchange_data = exchange_response.json()
            rates = exchange_data.get('rates', {})
            
            updated_count = 0
            new_count = 0
            
            for country_data in countries_data:
                name = country_data.get('name')
                capital = country_data.get('capital')
                region = country_data.get('region')
                population = country_data.get('population')
                flag_url = country_data.get('flag')
                
                # Handle currency information
                currencies = country_data.get('currencies', [])
                currency_code = None
                exchange_rate = None
                estimated_gdp = 0
                
                if currencies and len(currencies) > 0:
                    currency_code = currencies[0].get('code')
                    if currency_code in rates:
                        exchange_rate = rates[currency_code]
                        # Calculate estimated GDP with random multiplier
                        multiplier = random.uniform(1000, 2000)
                        if exchange_rate and exchange_rate > 0:
                            estimated_gdp = (population * multiplier) / exchange_rate
                
                # Validate required fields
                if not name or not population:
                    continue
                
                # Update or create the country record
                country, created = Country.objects.update_or_create(
                    name__iexact=name,
                    defaults={
                        'name': name,
                        'capital': capital,
                        'region': region,
                        'population': population,
                        'currency_code': currency_code,
                        'exchange_rate': exchange_rate,
                        'estimated_gdp': estimated_gdp,
                        'flag_url': flag_url,
                        'last_refreshed_at': timezone.now()
                    }
                )
                
                if created:
                    new_count += 1
                else:
                    updated_count += 1
            
            # Update refresh status
            total_countries = Country.objects.count()
            refresh_time = timezone.now()
            
            RefreshStatus.objects.create(
                total_countries=total_countries,
                last_refreshed_at=refresh_time
            )
            
            # Generate summary image
            self.generate_summary_image(total_countries, refresh_time)
            
            return Response({
                'message': f'Successfully refreshed countries data',
                'total': total_countries,
                'updated': updated_count,
                'new': new_count,
                'last_refreshed_at': refresh_time
            })
            
        except requests.RequestException as e:
            api_name = 'Countries API' if 'restcountries' in str(e) else 'Exchange Rates API'
            return Response(
                {
                    'error': 'External data source unavailable',
                    'details': f'Could not fetch data from {api_name}'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
    
    def generate_summary_image(self, total_countries, refresh_time):
        # Create directory if it doesn't exist
        cache_dir = os.path.join(settings.BASE_DIR, 'cache')
        os.makedirs(cache_dir, exist_ok=True)
        
        # Get top 5 countries by GDP
        top_countries = Country.objects.filter(estimated_gdp__isnull=False).order_by('-estimated_gdp')[:5]
        
        # Create the figure and axes
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.suptitle(f'Countries Data Summary - {refresh_time.strftime("%Y-%m-%d %H:%M:%S")}')
        
        # Plot total countries count
        ax1.bar(['Total Countries'], [total_countries], color='blue')
        ax1.set_title(f'Total Countries: {total_countries}')
        ax1.set_ylabel('Count')
        
        # Plot top 5 GDP countries
        if top_countries:
            country_names = [country.name for country in top_countries]
            country_gdps = [country.estimated_gdp / 1e9 for country in top_countries]  # Convert to billions
            
            ax2.bar(country_names, country_gdps, color='green')
            ax2.set_title('Top 5 Countries by Estimated GDP')
            ax2.set_ylabel('GDP (Billions USD)')
            ax2.tick_params(axis='x', rotation=45)
            
        plt.tight_layout()
        
        # Save the plot
        plt.savefig(os.path.join(cache_dir, 'summary.png'))
        plt.close()


class ImageView(APIView):
    def get(self, request):
        image_path = os.path.join(settings.BASE_DIR, 'cache', 'summary.png')
        
        if os.path.exists(image_path):
            return FileResponse(open(image_path, 'rb'), content_type='image/png')
        else:
            return Response({'error': 'Summary image not found'}, status=status.HTTP_404_NOT_FOUND)
