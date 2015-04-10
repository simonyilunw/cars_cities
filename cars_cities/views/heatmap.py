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

DENSITY_HEATMAP_FIELDS = ('mpg', 'mpg2', 'score')
FINE_GRAIN_HEATMAP_FIELDS = {
    'car_density': 0.0001
}

class Heatmap(View):
    
    def get(self, request, cityid):
        field = request.GET.get('field')
        variable = request.GET.get('variable', '3')
        
        context = {}
        template = 'heatmap2.html' if field in DENSITY_HEATMAP_FIELDS else 'heatmap.html'
        
        if field == 'block_price_avg':
            try:
                data = pickle_load(path.join(settings.CACHE_DIR, 'block_data'))[int(cityid)]
            except Exception as e:
                context['error'] = e
            context['data'] = data
        elif field in ZIPCODE_FIELDS:
            try:
                context['zipcodes'] = pickle_load(path.join(settings.CACHE_DIR, 'zipcodes/pickled/%s' % cityid))
            except IOError as e:
                context['error'] = e
           # print context['zipcodes']['94108']
        elif field in DENSITY_HEATMAP_FIELDS or field in FINE_GRAIN_HEATMAP_FIELDS:
            try:
                data = pickle_load(path.join(settings.LATLNGS_DIR, str(cityid)))
            except Exception as e:
                context['error'] = e
            else:
                context['data'] = data
        elif field == 'crime_rates' or field == 'crime_preds':
            try:
                context['zipcodes'] = pickle_load(path.join(settings.CACHE_DIR, 'zipcodes/pickled/%s' % cityid))
                if field == 'crime_rates':
                    data = pickle_load(path.join(settings.CACHE_DIR, 'crimeVisualization'))[int(cityid)]['crime_rates']

                else:
                    data = pickle_load(path.join(settings.CACHE_DIR, 'crimeVisualization'))[int(cityid)]['crime_preds']
                

            except Exception as e:
                context['error'] = e
            else:
                context['crime'] = data
                for zipcode, d in context['zipcodes'].iteritems():
                	if zipcode in context['crime']:
                		context['zipcodes'][zipcode]['crime'] = context['crime'][zipcode]
                #print context['zipcodes'].keys()

                #print data
        elif field == 'actual' or field == 'predicted':
            
            try:
                context['zipcodes'] = pickle_load(path.join(settings.CACHE_DIR, 'zipcodes/pickled/%s' % cityid))
            
                data = pickle_load(path.join(settings.STATS_DIR, 'demog'))

    
            except Exception as e:
                context['error'] = e
            else:

            	if str(cityid) == '153':
            		zipcodes = Reader(path.join(settings.MA_DATA_DIR, 'ma_zipcodes_poly_latlng'))
            		for sr in zipcodes.shapeRecords():
            			if sr.record[2] == 'Boston':
            				context['zipcodes'][sr.record[1]] = {}
                for zipcode, d in context['zipcodes'].iteritems():
                	
                    if zipcode in data and data[zipcode]['census'][int(variable)] != -1:
                    	if field == 'actual':
                        	context['zipcodes'][zipcode]['demog'] = data[zipcode]['census'][int(variable)]
                        if field == 'predicted':
                        	context['zipcodes'][zipcode]['demog'] = data[zipcode]['preds'][int(variable)]
                        #print context['zipcodes'][zipcode]['demog']
            

        else:
            try:
                data = Reader(path.join(settings.LATLNGS_SHP_DIR, str(cityid)))
            except Exception as e:
                context['error'] = e
            else:
                context['data'] = data
        
        if 'error' in context:
            return render(request, 'heatmap.html', context)

        polygon_path = path.join(settings.SAMPLES_DIR, 'polygons', str(cityid))
        polygon = pickle_load(polygon_path)
        if not self.request.GET.get('show_city_boundary') and 'data' in polygon:
            polygon.pop('data')
        context['polygon'] = polygon
        
        if field:
            print 'Using field ', field
            context['field'] = field
        if variable:
            context['vari'] = int(variable)
        if cityid:
            context['cityid'] = int(cityid)

        
        # special case boston to use MA data challenge data
        if str(cityid) == '153' and (field in ZIPCODE_FIELDS):
            zipcodes = Reader(path.join(settings.MA_DATA_DIR, 'ma_zipcodes_poly_latlng'))
            attribute_data = pickle_load(path.join(settings.CACHE_DIR, ZIPCODE_FIELDS[field]))
            zipcode_dict = dict((self.int_to_zipcode(zipcode), attribute) for (zipcode, attribute) in attribute_data)
            zipcode_data = dict([(sr.record[1], {
                'polygon': map(lambda x: list(x[::-1]), sr.shape.points), 
                'income': zipcode_dict[sr.record[1]],
                'price': zipcode_dict[sr.record[1]],
            }) for sr in zipcodes.shapeRecords() if sr.record[2] == 'Boston' and sr.record[1] != '02163'])
            context['zipcodes'] = zipcode_data

        if str(cityid) == '153' and (field == 'crime_rates' or field == 'crime_preds'):
            zipcodes = Reader(path.join(settings.MA_DATA_DIR, 'ma_zipcodes_poly_latlng'))
            zipcode_dict = context['crime']
            #print zipcode_dict.keys()
            zipcode_data = dict([(sr.record[1], {
                'polygon': map(lambda x: list(x[::-1]), sr.shape.points), 
                'crime': zipcode_dict[sr.record[1]],
            }) for sr in zipcodes.shapeRecords() if sr.record[2] == 'Boston' and sr.record[1] in zipcode_dict])
            context['zipcodes'] = zipcode_data

        #print context['zipcodes'].keys()

        if str(cityid) == '153' and (field == 'actual' or field == 'predicted'):
            zipcodes = Reader(path.join(settings.MA_DATA_DIR, 'ma_zipcodes_poly_latlng'))
        
            #print zipcode_dict.keys()
            zipcode_data = dict([(sr.record[1], {
                'polygon': map(lambda x: list(x[::-1]), sr.shape.points), 
                'demog': context['zipcodes'][sr.record[1]]['demog'],
            }) for sr in zipcodes.shapeRecords() if sr.record[2] == 'Boston' and sr.record[1] in context['zipcodes'] and 'demog' in context['zipcodes'][sr.record[1]]])
            context['zipcodes'] = zipcode_data

   
        
        context['zipcode_fields'] = ZIPCODE_FIELDS
        context['density_heatmap_fields'] = DENSITY_HEATMAP_FIELDS

        return render(request, template, context)
    
    def int_to_zipcode(self, n):
        n = str(n)
        while len(n) < 5: n = '0' + n
        return n

    def getRace(self, x):
        maxValue = max(x[16:19])
        if x[16] == maxValue:
            return 1
        elif x[17] == maxValue:
            return 2
        elif x[18] == maxValue:
            return 3

    def getEdu(self, x):
        maxValue = max([x[20], x[22], x[23]])
        if x[20] == maxValue:
            return 1
        elif x[22] == maxValue:
            return 2
        elif x[23] == maxValue:
            return 3