from os import path

from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings

from ...constants import ALL_CARS_DB, GEOCARS_DB
from ...utils.files import pickle_save, pickle_load


class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        cursor = connections[GEOCARS_DB].cursor()
        cursor.execute('select * from car_metadata')
        group_raw_data = cursor.fetchall()
        groups = {}
        for row in group_raw_data:
            groups[row[0]] = {
                'price': row[1],
                'fuel_type': row[2],
                'mpg_highway': row[3],
                'mpg_city': row[4],
                'hybrid': row[5],
                'electric': row[6],
                'country': row[7],
                'is_foreign': row[8],
                'price_bracket': row[9],
                'fine_price_bracket': row[10],
                'tg_price_bracket': row[11],
                'country_id': row[12],
                'make_id': row[13],
                'submodel_id': row[14]
            }
        
        for cityid in args or settings.CITY_IDS:
            if path.exists(path.join(settings.LATLNGS_DIR, str(cityid))):
                self.stdout.write('City %s already has latlngs, skipping' % cityid)
                continue
            
            self.stdout.write('Checking if city %s data file has mpg_weighted...' % cityid)
            
            try:
                data = pickle_load(path.join(settings.LATLNGS_DIR, str(cityid)))
            except:
                self.stderr.write('Cannot load data file... preparing to query')
            else:
                values = data.values()
                if values and 'mpg_weighted' in values[0]:
                    self.stdout.write('Already has it. Skipping to next')
                    continue
            self.compute_latlngs_for_city(str(cityid), groups)
    
    def compute_latlngs_for_city(self, city_id, groups):
        self.stdout.write('Querying data for %s...' % city_id)
        cursor = connections[ALL_CARS_DB].cursor()
        cursor.execute('select lat, lng, group_id, score from city_%s' % city_id)
        raw_data = cursor.fetchall()
        cursor.close()
        self.stdout.write('Query complete for %s, starting transform' % city_id)
        
        latlngs = {}
        total = len(raw_data)
        count = 0
        
        for lat, lng, group_id, score in raw_data:
            count += 1
            if count % 10000 == 0:
                self.stdout.write('Processed %s of %s rows' % (count, total))
                
            if (lat, lng) not in latlngs:
                latlngs[(lat, lng)] = {
                    'price': 0.0,
                    'mpg_highway': 0.0,
                    'mpg_city': 0.0,
                    'hybrid': 0.0,
                    'electric': 0.0,
                    'is_foreign': 0.0,
                    'total_score': 0.0,
                    'mpg_weighted': 0.0,
                }
            
            group_data = groups[group_id]
            latlngs[(lat, lng)]['total_score'] += score
            latlngs[(lat, lng)]['price'] += group_data['price'] * score
            latlngs[(lat, lng)]['mpg_highway'] += group_data['mpg_highway'] * score
            latlngs[(lat, lng)]['mpg_city'] += group_data['mpg_city'] * score
            latlngs[(lat, lng)]['hybrid'] += group_data['hybrid'] * score
            latlngs[(lat, lng)]['electric'] += group_data['electric'] * score
            latlngs[(lat, lng)]['is_foreign'] += group_data['is_foreign'] * score
            latlngs[(lat, lng)]['mpg_weighted'] += float(score) / group_data['mpg_city']
            
            #    for field in ['fuel_type', 'country', 'price_bracket', 'fine_price_bracket', 'tg_price_bracket', 'country_id', 'make_id', 'submodel_id']:
            #    self.add_counter(latlngs[(lat, lng)], field, group_data[field], score)
        
        for (lat, lng) in latlngs:
            latlngs[(lat, lng)]['price'] /= latlngs[(lat, lng)]['total_score']
            latlngs[(lat, lng)]['mpg_highway'] /= latlngs[(lat, lng)]['total_score']
            latlngs[(lat, lng)]['mpg_city'] /= latlngs[(lat, lng)]['total_score']
             
        self.stdout.write('Transform complete for %s, writing data file' % city_id)
        pickle_save(latlngs, path.join(settings.LATLNGS_DIR, str(city_id)))
    
    def add_counter(self, latlngs, name, value, score):
        if name not in latlngs:
            latlngs[name] = {}
        if value not in latlngs[name]:
            latlngs[name][value] = 0.0
        latlngs[name][value] += score
