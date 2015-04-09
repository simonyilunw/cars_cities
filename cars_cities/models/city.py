from os import path
from collections import defaultdict

from django.conf import settings

from base import BaseModel

from ..constants import ALL_CARS_DB, GEOCARS_DB, GEO_DB
from ..utils.files import pickle_save, pickle_load


class City(BaseModel):
    def __init__(self, city_id, force_recompute=False):
        self.city_id = city_id

        data = pickle_load(path.join(settings.CITY_DIR, str(city_id)))

        if force_recompute or not data:
            self.compute_data()
        else:
            self.load_state(data)

    def save_state(self):
        pickle_save(self.__dict__, path.join(settings.CITY_DIR, str(self.city_id)))

    def load_state(self, data):
        for key, value in data.iteritems():
            setattr(self, key, value)

    def compute_data(self):
        self.fetch_metadata()

        QUERY = """
        SELECT group_id, score FROM city_%s
        """
        result = self.execute_query(QUERY, [self.city_id], ALL_CARS_DB)

        groups = defaultdict(dict)
        for group_id, score in result:
            if 'score' in groups[group_id]:
                groups[group_id]['score'] += score
            else:
                groups[group_id]['score'] = score

        QUERY = """
        SELECT * FROM car_metadata WHERE group_id IN %s
        """
        result = self.execute_query(QUERY, [groups.keys()], GEOCARS_DB)

        for group_id, price, fuel_type, mpg_highway, mpg_city, hybrid, electric, country, is_foreign in result:
            groups[group_id].update({
                'price': price,
                'fuel_type': fuel_type,
                'mpg_city': mpg_city,
                'mpg_highway': mpg_highway,
                'hybrid': hybrid,
                'electric': electric,
                'country': country,
                'is_foreign': is_foreign
            })
        pickle_save(groups, path.join(settings.GROUPS_DIR, str(self.city_id)))

    @property
    def groups(self):
        return pickle_load(path.join(settings.GROUPS_DIR, str(self.city_id)))


    def fetch_metadata(self):
        QUERY = """
        SELECT cityname, state, lat, lng FROM cities WHERE cityid=%s
        """
        result = self.execute_query(QUERY, [self.city_id], GEO_DB)

        assert len(result) == 1
        result = result[0]
        self.name = result[0]
        self.state = result[1]
        self.latitude = result[2]
        self.longitude = result[3]
