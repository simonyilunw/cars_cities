from os import path

from django.views.generic import View
from django.conf import settings
from django.shortcuts import render

from ..models import City
from ..utils.files import pickle_save, pickle_load


class CountryHeatmap(View):

    def get(self, request):
        field = request.GET.get('field', 'race')


        context = {}
        if field:
            print 'Using field ', field
            context['field'] = field


        if field == 'race' or field == 'race_preds' or field == 'edu' or field == 'edu_preds' or field == 'income' or field == 'income_preds':

            try:
                context['zipcodes'] = pickle_load(path.join(settings.CACHE_DIR, 'zipcodes/pickled/allCities'))
            
                data = pickle_load(path.join(settings.STATS_DIR, 'demog'))

    
            except Exception as e:
                context['error'] = e
            else:
                for zipcode, d in context['zipcodes'].iteritems():
                
                    if zipcode in data:
                        if field == 'income':
                            context['zipcodes'][zipcode]['demog'] = data[zipcode]['census'][11]
                        elif field == 'income_preds':
                            context['zipcodes'][zipcode]['demog'] = data[zipcode]['preds'][11]
                        elif field == 'race':
                            context['zipcodes'][zipcode]['demog'] = self.getRace(data[zipcode]['census'])
                        elif field == 'race_preds':
                            context['zipcodes'][zipcode]['demog'] = self.getRace(data[zipcode]['preds'])
                        elif field == 'edu':
                            context['zipcodes'][zipcode]['demog'] = self.getEdu(data[zipcode]['census'])
                        elif field == 'edu_preds':
                            context['zipcodes'][zipcode]['demog'] = self.getEdu(data[zipcode]['preds'])
                        #print context['zipcodes'][zipcode]['demog']




        
        
        
        return render(request, 'countryheatmap.html', context)


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