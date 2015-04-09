from os import path

from django.views.generic import TemplateView
from django.conf import settings

from ..utils.files import pickle_load

import shapefile


class Results(TemplateView):
    template_name = 'results.html'

    def get_context_data(self, **kwargs):
        cities = pickle_load(path.join(settings.STATS_DIR, 'all_cities'))
        for city in cities:
            city['hotspots_available'] = path.isfile(
                path.join(settings.HOTSPOTS_DIR, str(city['cityid']) + '_hotspots.shp'))
            city['latlng_data_available'] = path.isfile(
                path.join(settings.LATLNGS_DIR, str(city['cityid'])))
            city['zipcode_available'] = path.isfile(
                path.join(settings.CACHE_DIR, 'zipcodes', 'pickled', str(city['cityid'])))
        kwargs['cities'] = cities
        kwargs['makes'] = pickle_load(path.join(settings.STATS_DIR, 'makes'))
        kwargs['models'] = pickle_load(path.join(settings.STATS_DIR, 'models'))
        kwargs['countries'] = pickle_load(
            path.join(settings.STATS_DIR, 'countries'))
        return kwargs
