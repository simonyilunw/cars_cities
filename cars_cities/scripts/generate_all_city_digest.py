from os import path
import sys
import us

import cPickle as pickle

from constants import CACHE_DIR, STATS_DIR, CITY_IDS, CITY_DIR, GROUPS_DIR, SAMPLES_DIR
from cars_cities.models import City

from utils import pickle_load

digest = []

for cityid in CITY_IDS:
    city = City(cityid)
    print 'Processing', city.name, city.state
    name = city.name.title()
    state = city.state.title()
    area = city.area
    samples = city.samples

    polygon_path = path.join(SAMPLES_DIR, 'polygons', str(cityid))
    polygon = pickle.load(open(polygon_path, 'r'))
    sample_area = polygon['area']

    coverage = float(sample_area) / float(area)

    moran_indices = pickle_load(path.join(CACHE_DIR, 'moran_indices'))

    digest.append({
        'cityid': cityid,
        'name': name,
        'state': state,
        'area': area,
        'samples': samples,
        'sample_area': sample_area,
        'coverage': coverage,
        'moran_index': moran_indices[cityid]
    })

pickle.dump(digest, open(path.join(STATS_DIR, 'all_cities'), 'wb'))
print 'FINISHED'
