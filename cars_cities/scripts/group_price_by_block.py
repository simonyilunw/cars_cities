from os import path
from collections import defaultdict

import shapefile

from utils import pickle_save, pickle_load
from constants import CACHE_DIR, LATLNGS_SHP_DIR

try:
    BLOCK_DATA_CACHE = pickle_load(path.join(CACHE_DIR, 'block_data'))
except Exception as e:
    print 'CANNOT LOAD BLOCK DATA CACHE: ', str(e)
    BLOCK_DATA_CACHE = {}


def get_block_id(data):
    return data['Block']['FIPS'][:-1]

def group_price_by_block(cityid):
    reader = shapefile.Reader(path.join(LATLNGS_SHP_DIR, str(cityid)))

    changed = False
    block_total = {}
    block_data = BLOCK_DATA_CACHE[cityid]

    for sr in reader.shapeRecords():
        (lng, lat) = sr.shape.points[0]
        data = block_data.get((lat, lng))

        if not data:
            continue

        if 'price' not in data and 'income' not in data:
            block_data[(lat, lng)]['price'] = sr.record[0]
            block_data[(lat, lng)]['income'] = sr.record[1]
            changed = True
        if 'Block' in data:
            if get_block_id(data) in block_total:
                block_total[get_block_id(data)]['total'] += float(sr.record[0])
                block_total[get_block_id(data)]['count'] += 1
            else:
                block_total[get_block_id(data)] = {
                    'total': float(sr.record[0]),
                    'count': 1
                }

    block_averages = {k: v['total'] / v['count'] for k, v in block_total.iteritems()}
    print len(block_data)
    print len(block_averages)

    for key, data in block_data.iteritems():
        if 'Block' in data:
            data['block_price_average'] = block_averages[get_block_id(data)]
            changed = True

    if changed:
        print 'CHANGED! updating block cache file'
        pickle_save(BLOCK_DATA_CACHE, path.join(CACHE_DIR, 'block_data'))

if __name__ == '__main__':
    group_price_by_block(153)
