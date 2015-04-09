from os import path

from django.views.generic import View
from django.conf import settings
from django.shortcuts import render

from ..utils.files import pickle_load
from ..utils.shapefile import Reader


ZIPCODE_FIELDS = {
    'zipcode_price_avg': 'zip_code_to_car_price',
    'zipcode_income_avg': 'zip_code_to_income'
}

FINE_GRAIN_HEATMAP_FIELDS = {
    'car_density': 0.0001
}

class Voting(View):
    
    def get(self, request, cityid):
        field = request.GET.get('field', 'voting')
        
        context = {}
        template = 'voting.html' 
        
        polygon_path = path.join(settings.SAMPLES_DIR, 'polygons', str(cityid))
        polygon = pickle_load(polygon_path)
        if not self.request.GET.get('show_city_boundary') and 'data' in polygon:
            polygon.pop('data')
        context['polygon'] = polygon

        voting = Reader(path.join(settings.CACHE_DIR, 'arcgis/voting_result_new'))
        # print voting.fields[36]

        if field == 'voting':
            voting_data = dict([(sr.record[36], {
                'polygon': map(lambda x: list(x[::-1]), sr.shape.points), 
                'voting': sr.record[37],
            }) for sr in voting.shapeRecords() ])
        elif field == 'voting_preds':
            voting_data = dict([(sr.record[36], {
                'polygon': map(lambda x: list(x[::-1]), sr.shape.points), 
                'demo': sr.record[38],
            }) for sr in voting.shapeRecords() ])
        
        print len(voting_data)
        #for sr in voting.shapeRecords():
        #    print sr.record


        
        context['voting'] = voting_data
        context['field'] = field

   
        
        return render(request, template, context)
    
 