from os import path

from django.views.generic import TemplateView
from django.conf import settings

from ..utils.files import pickle_load


class Home(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        cities = pickle_load(path.join(settings.STATS_DIR , 'all_cities'))
        aggregate = pickle_load(path.join(settings.STATS_DIR, 'aggregate'))
        kwargs['cities'] = cities
        kwargs['aggregate'] = aggregate
        return kwargs
        