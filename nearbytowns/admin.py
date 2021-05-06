from django.contrib import admin
from django.contrib.gis.admin import OSMGeoAdmin
from .models import Town, Search


@admin.register(Town)
class TownAdmin(OSMGeoAdmin):
    list_display = ('name', 'location')

admin.site.register(Search)