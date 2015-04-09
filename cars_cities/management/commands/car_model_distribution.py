from os import path
from collections import defaultdict

import shapefile

from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings

from ...constants import GEOCARS_DB
from ...utils.files import pickle_save

QUERY = """
select 
cc.make,
cc.model,
cc.submodel,
t1.score
from all_cars.city_%s t1 
    join geocars.car_metadata t2 on t1.group_id=t2.group_id 
    join geocars_crawled.control_classes cc on t2.group_id=cc.group_id 
where %s
group by t1.lat, t1.lng;
"""

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading SHP file...')
        reader = shapefile.Reader(path.join(settings.CACHE_DIR, 'government', 'new_mexico_clipped'))

        make_distribution = defaultdict(float)
        model_distribution = defaultdict(float)
        submodel_distribution = defaultdict(float)

        filter_clause = []
        for shape in reader.shapes():
            lng, lat = shape.points[0]
            filter_clause.append(('(t1.lat=%s and t1.lng=%s)' % (lat, lng)))

        print '%s filter clauses!' % len(filter_clause)
        segment = 0
        increment = 500
        raw_data = []
        segments = len(filter_clause) / increment

        while segment * increment < len(filter_clause):
            filter_string = ' or '.join(filter_clause[segment * increment:segment * increment + increment])
            print 'Quering segment %d out of %s' % (segment, segments)
            self.stdout.write('Querying data...')
            cursor = connections[GEOCARS_DB].cursor()
            cursor.execute(QUERY % (173, filter_string))
            raw_data += cursor.fetchall()
            cursor.execute(QUERY % (174, filter_string))
            raw_data += cursor.fetchall()
            segment += 1

        for make, model, submodel, score in raw_data:
            make_distribution[make] += score
            model_distribution[model] += score
            submodel_distribution[submodel] += score

        make_distribution = sorted(make_distribution.items(), key=lambda x: x[1], reverse=True)
        print '\nMake Distribution:'
        for make, score in make_distribution:
            print '%s: %s' % (make.title(), score)

        model_distribution = sorted(model_distribution.items(), key=lambda x: x[1], reverse=True)
        print '\nModel Distribution:'
        for model, score in model_distribution:
            print '%s: %s' % (model.title(), score)

        submodel_distribution = sorted(submodel_distribution.items(), key=lambda x: x[1], reverse=True)
        print '\nSubmodel Distribution:'
        for submodel, score in submodel_distribution:
            print '%s: %s' % (submodel.title(), score)

        """
        makes = defaultdict(float)
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

        """
        self.stdout.write('Finished!')
