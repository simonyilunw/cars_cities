from django.core.management.base import BaseCommand
from django.db import connections

from ...constants import ALL_CARS_DB, GEO_DB
from ...models import City


class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        cursor = connections[ALL_CARS_DB].cursor()
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()
        cursor.close()
        
        samples = {}
        if 'get_sample_count' in args:
            self.stdout.write('Querying for sample count...')
            cursor = connections[GEO_DB].cursor()
            cursor.execute('SELECT cityid, COUNT(*) from samples where sampled=1 group by cityid')
            samples = dict(cursor.fetchall())
            cursor.close()
            self.stdout.write('Sample query complete')
            
        for (table, ) in tables:
            split = table.split('_')
            if len(split) != 2:
                continue
            city_id = split[1]
            self.stdout.write('Computing city %s...' % city_id)
            city_id = int(city_id)
            city = City(city_id)
            
            if samples and city_id in samples:
                city.samples = samples[city_id]
                city.save_state()
                self.stdout.write('City %s state updated with samples' % city_id)
