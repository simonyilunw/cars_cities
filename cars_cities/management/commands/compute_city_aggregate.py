from os import path

from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings

from ...constants import GEOCARS_DB
from ...utils.files import pickle_save, pickle_load

QUERY = """
select 
stddev(t2.price*t1.score) as std_price, 
stddev(t2.mpg_city*t1.score) as std_mpg_city,
stddev(t2.mpg_highway*t1.score) as std_mpg_highway, 
sum(t1.score)/sum(t2.mpg_highway*t1.score) as avg_gpm_highway, 
sum(t1.score)/sum(t2.mpg_city*t1.score) as avg_gpm_city, 
stddev(t2.hybrid*t1.score) as std_hybrid, 
stddev(t2.is_foreign*t1.score) as std_foreign, 
stddev(t2.electric*t1.score) as std_electric
from all_cars.city_%s t1 join geocars.car_metadata t2 on t1.group_id = t2.group_id 
"""

CUSTOM_CITIES = {}

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        for city_id in CUSTOM_CITIES or settings.CITY_IDS:
            self.compute_latlng_for_city(city_id)

    def compute_latlng_for_city(self, city_id):
        self.stdout.write('Querying data for %s...' % city_id)
        cursor = connections[GEOCARS_DB].cursor()
        cursor.execute(QUERY % city_id)
        raw_data = cursor.fetchall()
        self.stdout.write('Finished querying data for %s, starting pickling...' % city_id)

        aggregate = pickle_load(path.join(settings.STATS_DIR, 'aggregate'))
        count = 0
        if city_id not in aggregate:
            aggregate[city_id] = {}

        for std_price, std_mpg_city, std_mpg_highway, avg_gpm_highway, avg_gpm_city, \
            std_hybrid, std_foreign, std_electric in raw_data:
            aggregate[city_id]['std_price'] = std_price
            aggregate[city_id]['std_mpg_city'] = std_mpg_city
            aggregate[city_id]['std_mpg_highway'] = std_mpg_highway
            aggregate[city_id]['avg_gpm_highway'] = avg_gpm_highway
            aggregate[city_id]['avg_gpm_city'] = avg_gpm_city
            aggregate[city_id]['std_hybrid'] = std_hybrid
            aggregate[city_id]['std_foreign'] = std_foreign
            aggregate[city_id]['std_electric'] = std_electric

            count += 1
            self.stdout.write('Pickled %s rows..' % count)
            if count > 1:
                self.stderr.write('How did there appear more than 1 row??')

        self.stdout.write('Pickling complete for %s, writing data file..' % city_id)
        pickle_save(aggregate, path.join(settings.STATS_DIR, 'aggregate'))
        self.stdout.write('Finished!')
