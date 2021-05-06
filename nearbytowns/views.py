from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from django.contrib.gis.geos import fromstr
#from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point
from .models import Town, Search
from .forms import SearchForm
import folium
import geocoder

# Create your views here.
def index(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/')
    else:
        form = SearchForm() 
    address = Search.objects.all().last()
    location = geocoder.osm(address)
    lat = location.lat
    lng= location.lng
    name = location.address

    if lat == None or lng == None:
        address.delete()
        return HttpResponse('Your address/coordinates input is invalid')
    #create a map object
    m = folium.Map(width=2000,height=740,location=[5.636114, -0.184089], zoom_start=12)
    folium.Marker([lat, lng]).add_to(m)
    folium.Marker([lat, lng], tooltip='Last known location',
                   popup=name).add_to(m)

    print(f"checking distance from {lat} {lng}")
    town, town_loc = find_closest_town(lat, lng)
    print(f"{town}")
    print(f"{town_loc}")
    # add a marker for the town

    folium.CircleMarker([town_loc.y, town_loc.x], tooltip='Closest town to last known location',color='#dc143c', fill_color='#dc143c',
         radius=6, weight=10,
                   popup=name).add_to(m)
    

    #get html representation of map object
    m = m._repr_html_()
    context = {
        'm' : m,
        'form' : form,
        'closest_town_name' : town,
    }
    #template_name = 'towns/index.html'
    return render(request, 'towns/index.html', context)

def find_closest_town(lat, lng):
    all_towns = Town.objects.all()
    zip_location = Point(lng, lat, srid=4326)
    minimum_distance = 100000000
    closest_town = None
    for t in all_towns:
        #distance = Distance(t.location, zip_location)
        distance = t.location.distance(zip_location)
        if distance < minimum_distance:
            print(distance)
            print("new minimum distance")
            minimum_distance = distance
            closest_town = t
    #print(closest_town.name)
    #closest_town_loc = closest_town.location
    #print(closest_town_loc)
    
    return closest_town.name, closest_town.location

