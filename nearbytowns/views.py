from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import generic
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point
from .models import Town, Search
from .forms import SearchForm
import folium
from folium import plugins
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
    m = folium.Map(width=1450,height=700,location=[lat, lng], zoom_start=12, control_scale=True)

    #add tiles to map
    folium.raster_layers.TileLayer('Open Street Map').add_to(m)
    #folium.raster_layers.TileLayer('Stamen Terrain').add_to(m)
    folium.raster_layers.TileLayer('stamenterrain').add_to(m)
    folium.TileLayer(
        tiles = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr = 'Esri',
        name = 'Esri Satellite',
        overlay = False,
        control = True).add_to(m)

    #add layer control to show different maps
    folium.LayerControl().add_to(m)


    folium.Marker([lat, lng]).add_to(m)
    folium.Marker([lat, lng], tooltip='Last known location',
                   popup=name).add_to(m)

    print(f"checking distance from {lat} {lng}")
   
    #plot near towns to map
    closest_towns = find_closest_town(lat, lng)
    for town in closest_towns:
        print(town)
        folium.CircleMarker(location=town['coordinates'], popup=town['name'], tooltip='nearby town',
        color='#dc143c', radius=2, weight=10
        ).add_to(m)   

    #add measure control
    measure_control = plugins.MeasureControl(position='topright',
                                                    active_color='red',
                                                    completed_color='red',
                                                    primary_length_unit='kilometers'
                                                    )
    m.add_child(measure_control)

    #add a draw tool
    draw = plugins.Draw(export=True)
    draw.add_to(m)

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
    min_distance_towns_list = []
    for t in all_towns:
        distance = t.location.distance(zip_location)
        if distance < minimum_distance:
            town_dict = {'name': t.name, 'coordinates':(t.location.y, t.location.x), 'distance': distance}
            min_distance_towns_list.append(town_dict)
            minimum_distance = distance
    new_min_dist_towns = min_distance_towns_list[-4:]
    return new_min_dist_towns 


