from django.contrib import admin
from .models import Country, RefreshStatus
# Register your models here.


admin.site.register(Country)
admin.site.register(RefreshStatus)