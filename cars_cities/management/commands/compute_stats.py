import numpy as np

from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings

from ...constants import ALL_CARS_DB
from ...models import City
from ...utils.files import pickle_save


class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        cursor = connections[ALL_CARS_DB].cursor()
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()
        cursor.close()
        
        stats = {}
        for (table, ) in tables:
            split = table.split('_')
            if len(split) != 2:
                continue
            city_id = split[1]
            city = City(int(city_id))
            self.stdout.write('Computing stats for city %s... with %d samples' % (city_id, city.samples))
            stats[city.name] = self.compute_stats(city)
            stats[city.name].update({
                'latitude': city.latitude,
                'longitude': city.longitude,
                'total_samples': city.samples
            })
            
        pickle_save(stats, settings.STATS_DIR + '/aggregate')
        
    def compute_stats(self, city):
        stats = {}
        
        total_car_mpg_highway = 0.0
        total_score = 0.0
        total_hybrid = 0.0
        total_foreign = 0.0
        total_domestic = 0.0
        
        weighted_prices = []
        
        for group_id, data in city.groups.iteritems():
            score = data['score']
            raw_price = data['price']
            price = raw_price * score
            weighted_prices.append(price)
            total_score += score
            total_car_mpg_highway += data['mpg_highway'] * score
            if data['hybrid']:
                total_hybrid += score
            if data['is_foreign']:
                total_foreign += score
            else:
                total_domestic += score
                
        stats['total_cars'] = total_score
        stats['car_price_avg'] = sum(weighted_prices) / total_score
        stats['car_price_variance'] = np.var(weighted_prices)
        stats['car_mpg_highway_avg'] = total_car_mpg_highway / total_score
        stats['car_hybrid_ratio'] = total_hybrid / total_score
        stats['car_foreign_ratio'] = total_foreign / total_score
        stats['car_domestic_ratio'] = total_domestic / total_score
        return stats
    