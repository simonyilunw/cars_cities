from os import path


from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings

from ...constants import GEOCARS_DB
from ...utils.files import pickle_save

QUERY = """
select 
t1.lat, 
t1.lng, 
sum(t1.score) as total_score, 
sum(t2.price*t1.score)/sum(t1.score) as avg_price, 
sum(t2.mpg_highway*t1.score)/sum(t1.score) as avg_mpg_highway, 
sum(t2.mpg_city*t1.score)/sum(t1.score) as avg_mpg_city, 
sum(t2.hybrid*t1.score) as avg_hybrid, 
sum(t2.is_foreign*t1.score) as avg_foreign, 
sum(t2.electric*t1.score) as avg_electric, 
sum(t1.score/t2.mpg_city) as mpg_weighted,
t1.id
from all_cars.`city_%s` t1 join geocars.`car_metadata` t2 on t1.group_id = t2.group_id group by t1.lat, t1.lng;
"""

LAT = 0
LNG = 1
TOTAL_SCORE = 2
AVG_PRICE = 3
AVG_MPG_HIGHWAY = 4
AVG_MPG_CITY = 5
AVG_HYBRID = 6
AVG_FOREIGN = 7
AVG_ELECTRIC = 8
MPG_WEIGHTED = 9
DB_ID = 10

CUSTOM_CITIES = {174, 173}

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

        latlngs = {}
        count = 0
        for row in raw_data:
            lat, lng = float(row[LAT]), float(row[LNG])
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
            latlngs[(lat, lng)]['id'] = row[DB_ID]
            latlngs[(lat, lng)]['total_score'] = row[TOTAL_SCORE]
            latlngs[(lat, lng)]['price'] = row[AVG_PRICE]
            latlngs[(lat, lng)]['mpg_highway'] = row[AVG_MPG_HIGHWAY]
            latlngs[(lat, lng)]['mpg_city'] = row[AVG_MPG_CITY]
            latlngs[(lat, lng)]['hybrid'] = row[AVG_HYBRID]
            latlngs[(lat, lng)]['electric'] = row[AVG_ELECTRIC]
            latlngs[(lat, lng)]['is_foreign'] = row[AVG_FOREIGN]
            latlngs[(lat, lng)]['mpg_weighted'] = row[MPG_WEIGHTED]

            count += 1
            if count % 3000 == 0:
                self.stdout.write('Pickled %s rows..' % count)

        self.stdout.write('Pickling complete for %s, writing data file..' % city_id)
        pickle_save(latlngs, path.join(settings.LATLNGS_DIR, str(city_id)))
        self.stdout.write('Finished!')
