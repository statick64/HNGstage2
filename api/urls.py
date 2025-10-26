from django.urls import path
from .views import (
    CountryListView,
    CountryDetailView,
    StatusView,
    RefreshCountriesView,
    ImageView
)

urlpatterns = [
    path('countries/', CountryListView.as_view(), name='country-list'),
    path('countries/<str:name>/', CountryDetailView.as_view(), name='country-detail'),
    path('countries/refresh', RefreshCountriesView.as_view(), name='country-refresh'),
    path('status/', StatusView.as_view(), name='status'),
    path('countries/image/', ImageView.as_view(), name='country-image'),
]
