from os import path

from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings

from ...constants import GEOCARS_DB
from ...utils.files import pickle_save, pickle_load

MAKES_QUERY = """
select 
car.make,
car.%s,
sum(sample.score)
from all_cars.city_%s sample join geocars_crawled.control_classes car on sample.group_id = car.group_id
where car.make='Aston Martin' or car.make='Land Rover' or car.make='AM General' group by car.make, car.%s
"""

COUNTRIES_QUERY = """
select 
car.country,
sum(sample.score)
from all_cars.city_%s sample join geocars.car_metadata car on sample.group_id = car.group_id
group by car.country
"""

CUSTOM_CITIES = {}


class Command(BaseCommand):

    def write_countries(self):
        cursor = connections[GEOCARS_DB].cursor()
        cursor.execute(
            'select distinct country from geocars.car_metadata')
        raw_data = cursor.fetchall()
        countries = [str(r[0]) for r in raw_data]
        self.stdout.write(str(countries))
        pickle_save(countries, path.join(settings.STATS_DIR, 'countries'))
        self.stdout.write('Written to countries file')

    def write_makes(self):
        cursor = connections[GEOCARS_DB].cursor()
        cursor.execute(
            'select distinct make from geocars_crawled.control_classes')
        raw_data = cursor.fetchall()
        makes = [str(r[0]) for r in raw_data]
        self.stdout.write(str(makes))
        pickle_save(makes, path.join(settings.STATS_DIR, 'makes'))
        self.stdout.write('Written to makes file')

    def write_models(self):
        cursor = connections[GEOCARS_DB].cursor()
        cursor.execute(
            'select make, model from geocars_crawled.control_classes group by make, model')
        raw_data = cursor.fetchall()
        models = {}

        for make, model in raw_data:
            if make not in models:
                models[make] = []
            models[make].append(model)

        for m in models.values():
            m = sorted(m)

        self.stdout.write(str(models))
        pickle_save(models, path.join(settings.STATS_DIR, 'models'))
        self.stdout.write('Written to models file')

    def fix_aggregate_from_backup(self):
        aggregate = pickle_load(path.join(settings.STATS_DIR, 'aggregate'))
        backup = pickle_load(
            path.join(settings.STATS_DIR, 'aggregate_backup_12-10-2014'))

        for cityid in backup:
            makes = backup[cityid]['makes']
            models = backup[cityid]['models']

            for make in makes:
                if make not in aggregate[cityid]['makes']:
                    aggregate[cityid]['makes'][make] = makes[make]
                    self.stdout.write(
                        'Syncing make %s from city %s' % (make, cityid))

            for model in models:
                if model not in aggregate[cityid]['models']:
                    aggregate[cityid]['models'][model] = models[model]
                    self.stdout.write(
                        'Syncing model %s from city %s' % (model, cityid))

        pickle_save(aggregate, path.join(settings.STATS_DIR, 'aggregate'))

    def handle(self, *args, **kwargs):
        self.fix_aggregate_from_backup()
        return
        for city_id in CUSTOM_CITIES or settings.CITY_IDS:
            self.compute_car_aggregate_for_city(city_id)

    def compute_car_aggregate_for_city(self, city_id):
        self.stdout.write('Loading aggregate data...')

        aggregate = pickle_load(path.join(settings.STATS_DIR, 'aggregate'))

        cursor = connections[GEOCARS_DB].cursor()
        self.stdout.write('Querying %s data for %s...' % ('country', city_id))
        cursor.execute(COUNTRIES_QUERY % city_id)
        raw_data = cursor.fetchall()
        self.stdout.write(
            'Finished querying data for %s, starting pickling...' % city_id)

        if city_id not in aggregate:
            aggregate[city_id] = {}

        aggregate[city_id]['countries'] = {}
        for country, score in raw_data:
            aggregate[city_id]['countries'][country] = score

        self.stdout.write(
            'Pickling complete for %s, writing data file..' % city_id)
        pickle_save(aggregate, path.join(settings.STATS_DIR, 'aggregate'))
        self.stdout.write('Finished!')
