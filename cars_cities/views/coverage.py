from os import path

from django.views.generic import TemplateView
from django.conf import settings

from ..utils.files import pickle_load


class Coverage(TemplateView):
    template_name = 'coverage.html'
    
    def get_context_data(self, **kwargs):
        cities = pickle_load(path.join(settings.STATS_DIR , 'all_cities'))
        kwargs['cities'] = cities
        return kwargs
        