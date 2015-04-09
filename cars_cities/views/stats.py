from django.views.generic import TemplateView
from django.conf import settings

from ..utils.files import pickle_load


class Stats(TemplateView):
    template_name = 'stats.html'
    
    def get_context_data(self, **kwargs):
        cities = pickle_load(settings.STATS_DIR + '/aggregate')
        kwargs.update({
            'cities': cities
        })
        return kwargs
