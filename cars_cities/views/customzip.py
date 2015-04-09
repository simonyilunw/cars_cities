from os import path

from django.views.generic import View
from django.conf import settings
from django.shortcuts import render

from ..utils.files import pickle_load
from ..utils.shapefile import Reader

class CustomZip(View):
    
    def get(self, request):
        cityid = int(request.GET.get('cityid'))
        fname = request.GET.get('fname')
        
        context = {}
        template = 'customzip.html'

        try:
            zip_dict = {}
            poly_dict = pickle_load(path.join(settings.CACHE_DIR, 'zipcodes/pickled/%d' % cityid))
            if fname.endswith('pkl'):
              # Handle pickle files
              # Get dictionary of zipcode -> color for zipcodes in the city
              custom_data = pickle_load(path.join(settings.CACHE_DIR, 'zipcodes', 'custom', fname))
              custom_dict = custom_data['zip_map'] # {cityid: {zipcode(%05d):(r,g,b)}}
              attr_name = custom_data['att_name']
            elif fname.endswith('.txt'):
                # Handle text files
                custom_dict = {cityid:{}}
                with open(path.join(settings.CACHE_DIR, 'zipcodes', 'custom', fname), 'r') as in_file:
                    line = in_file.readline()
                    line = line.strip().split(',')
                    for i in range(0, len(line), 2):
                      if line[i] == 'att_name':
                        attr_name = line[i+1]
                    for line in in_file:
                        line = line.strip().split(',')
                        # city, zipcode, r, g, b
                        line_cityid = int(line[0])
                        if line_cityid == cityid:
                            zipcode = '%05d' % int(line[1])
                            r = int(line[2])
                            g = int(line[3])
                            b = int(line[4])
                            custom_dict[cityid][zipcode] = (r,g,b)
            for zipcode in poly_dict:
                if zipcode in custom_dict[cityid]:
                    rgb = custom_dict[cityid][zipcode]
                    zip_dict[zipcode] = {'polygon':poly_dict[zipcode]['polygon'], 'r':rgb[0], 'g':rgb[1], 'b':rgb[2]}
                elif int(zipcode) in custom_dict[cityid]:
                    rgb = custom_dict[cityid][int(zipcode)]
                    zip_dict[zipcode] = {'polygon':poly_dict[zipcode]['polygon'], 'r':rgb[0], 'g':rgb[1], 'b':rgb[2]}
            context['var_name'] = attr_name
            context['zipcodes'] = zip_dict
        except Exception as e:
            context['error'] = e
            return render(request, template, context)

 

        polygon_path = path.join(settings.SAMPLES_DIR, 'polygons', str(cityid))
        polygon = pickle_load(polygon_path)
        polygon.pop('data')
        context['polygon'] = polygon

        return render(request, template, context)
