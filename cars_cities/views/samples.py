from os import path

from django.views.generic import View
from django.conf import settings
from django.shortcuts import render

from ..utils.files import pickle_load


class Samples(View):
    
    def get(self, request, cityid=None):            
        polygon_path = path.join(settings.SAMPLES_DIR, 'polygons', str(cityid))
        polygon = pickle_load(polygon_path)
        city = pickle_load(path.join(settings.CITY_DIR, str(cityid)))
        
        if 'boundary' in city:
            city['boundary'] = [[y,x] for [x,y] in city['boundary']] # reverse the lat longs
            
        context = {
            'polygon': polygon,
            'city': city
        }
        return render(request, 'samples.html', context)
