from os import path

import shapefile

from django.views.generic import TemplateView
from django.conf import settings

from ..utils.files import pickle_load
from ..utils.shapefile import Reader


class Hotspots(TemplateView):
    template_name = 'hotspots.html'

    def get_context_data(self, **kwargs):
        cityid = self.kwargs.get('cityid')

        special = self.request.GET.get('special')

        if special:
            shp_path = path.join(
                settings.CACHE_DIR, 'hotspots', special)
        else:
            shp_path = path.join(
                settings.HOTSPOTS_DIR, str(cityid) + '_hotspots')

        try:
            reader = Reader(shp_path)
        except Exception as e:
            kwargs['error'] = e
            return kwargs

        zipcodes = Reader(
            path.join(settings.MA_DATA_DIR, 'ma_zipcodes_poly_latlng'))
        polygon_path = path.join(settings.SAMPLES_DIR, 'polygons', str(cityid))
        polygon = pickle_load(polygon_path)

        kwargs['data'] = reader
        kwargs['polygon'] = polygon
        kwargs['zipcodes'] = zipcodes
        return kwargs
