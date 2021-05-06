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
    m = folium.Map(width=2000,height=900,location=[5.636114, -0.184089], zoom_start=12)
    folium.Marker([lat, lng]).add_to(m)
    folium.Marker([lat, lng], tooltip='Click for more',
                   popup=name).add_to(m)
    print(f"checking distance from {lat} {lng}")
    town = find_closest_town(lat, lng)
    town_lat = town.lat
    town_lng = town.lng
    print(town_lng)
    print(f"{town}")
    
    folium.Marker([lat, lng], tooltip='Click for more',
                   popup=name).add_to(m)
    # add a marker for the town




    

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
    print(closest_town.name)
    
    return closest_town.name

#user_location = Point(lng, lat, srid=4326)

# location_ = geocoder.osm('Suhum')
# latitude = location_.lat
# longitude = location_.lng

# longitude = -2.32696929
# latitude = 6.46572529

# freds_house = Point(lng, lat, srid=4326)


# class Home(generic.ListView):
#     model = Town
#     context_object_name = 'towns'
#     queryset = Town.objects.annotate(distance_from_freds_house=Distance('location',freds_house)
#     ).order_by('distance')[0:4]
#     template_name = 'towns/index.html'
