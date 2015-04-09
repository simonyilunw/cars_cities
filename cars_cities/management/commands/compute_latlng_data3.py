from os import path


from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings

from ...constants import GEOCARS_DB
from ...utils.files import pickle_save, pickle_load

QUERY = """
select 
t1.lat, 
t1.lng, 
cc.make,
cc.model,
cc.submodel,
t1.score
from all_cars.city_%s t1 
    join geocars_crawled.control_classes cc on t1.group_id=cc.group_id 
where cc.make = 'mercedes-benz'
"""

LAT = 0
LNG = 1
MAKE = 2
MODEL = 3
SUBMODEL = 4
SCORE = 5

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        """
        cursor.execute('select distinct cc.make from car_metadata md join geocars_crawled.control_classes cc on md.group_id=cc.group_id')
        makes = sorted([s[0] for s in cursor.fetchall() if s[0]])

        cursor.execute('select distinct cc.model from car_metadata md join geocars_crawled.control_classes cc on md.group_id=cc.group_id')
        models = sorted([s[0] for s in cursor.fetchall() if s[0]])

        cursor.execute('select distinct cc.submodel from car_metadata md join geocars_crawled.control_classes cc on md.group_id=cc.group_id')
        submodels = sorted([s[0] for s in cursor.fetchall() if s[0]])
        """

        for city_id in [175] or settings.CITY_IDS:
            self.compute_latlng_for_city(city_id)

    def compute_latlng_for_city(self, city_id):
        self.stdout.write('Loading existing data for %s...' % city_id)
        latlngs = pickle_load(path.join(settings.LATLNGS_DIR, str(city_id)))

        self.stdout.write('Querying data for %s...' % city_id)
        cursor = connections[GEOCARS_DB].cursor()
        cursor.execute(QUERY % city_id)
        raw_data = cursor.fetchall()
        self.stdout.write('Finished querying data for %s, starting pickling...' % city_id)

        count = 0
        for row in raw_data:
            lat, lng = float(row[LAT]), float(row[LNG])
            if (lat, lng) not in latlngs:
                self.stderr.write('(%s, %s) not found in file! Make sure you run compute_latlng_data2 on %s first!' % (lat, lng, city_id))
                continue
            if 'makes' not in latlngs[(lat, lng)]:
                latlngs[(lat, lng)]['makes'] = {}
                latlngs[(lat, lng)]['models'] = {}
                latlngs[(lat, lng)]['submodels'] = {}
            latlngs[(lat, lng)]['makes'][row[MAKE]] = row[SCORE]
            latlngs[(lat, lng)]['models'][row[MODEL]] = row[SCORE]
            latlngs[(lat, lng)]['submodels'][row[SUBMODEL]] = row[SCORE]
            count += 1
            if count % 3000 == 0:
                self.stdout.write('Pickled %s rows..' % count)

        self.stdout.write('Pickling complete for %s, writing data file..' % city_id)
        pickle_save(latlngs, path.join(settings.LATLNGS_DIR, str(city_id)))
        self.stdout.write('Finished!')
