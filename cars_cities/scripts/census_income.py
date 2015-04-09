import sys
from os import path
import time

from census import Census, ALL
from fcc.census_block_conversions import census_block_dict

import shapefile
from constants import CACHE_DIR, LATLNGS_SHP_DIR
from utils import pickle_save, pickle_load

YEAR = 2010
try:
    BLOCK_DATA_CACHE = pickle_load(path.join(CACHE_DIR, 'block_data'))
except Exception as e:
    print 'CANNOT LOAD BLOCK DATA CACHE: ', str(e)
    sys.exit(1)
CENSUS_DATA_CACHE = pickle_load(path.join(CACHE_DIR, 'census_data_cache'))
CENSUS_API_KEY = '3a7f0def09f356fa48f84558824b09a009c1f6e2'
INCOME_VARIABLE = 'B06011_001E'
AGE_VARIABLE = 'B05004_004E'
client = Census(CENSUS_API_KEY).acs


def get_block_data(lat, lng, data):
    if not data.get((lat, lng)):
        data[(lat, lng)] = census_block_dict(lat, lng, year=YEAR)
    return data[(lat, lng)]


def get_variable(lat, lng, data, var=INCOME_VARIABLE):
    block_data = get_block_data(lat, lng, data)
    #print block_data
    try:
        state_fips = block_data['State']['FIPS']
        county_fips = block_data['County']['FIPS'][2:]
        tract_fips = block_data['Block']['FIPS'][5:11]
    except Exception as e:
        print 'Error getting block data for %s, %s' % (lat, lng)
        return 0
        
    query = (var, state_fips, county_fips, tract_fips)
    if query not in CENSUS_DATA_CACHE:
        result = client.state_county_tract(*query)[0]  
        CENSUS_DATA_CACHE[query] = result
    return CENSUS_DATA_CACHE[query][var]


def compute_city(cityid):
    reader = shapefile.Reader(path.join(LATLNGS_SHP_DIR, str(cityid)))
    writer = shapefile.Writer(shapefile.POINT)
    writer.autoBalance = 1
    writer.field('price', 'N')
    writer.field('income', 'N')
    writer.field('age', 'N')
    
    total = len(reader.shapeRecords())
    count = 0
    for sr in reader.shapeRecords():
        point = sr.shape.points[0]
        price = sr.record[0]
        income = get_variable(point[1], point[0], BLOCK_DATA_CACHE[cityid], INCOME_VARIABLE)
        age = get_variable(point[1], point[0], BLOCK_DATA_CACHE[cityid], AGE_VARIABLE)
        writer.point(point[0], point[1])
        writer.record(price, income, age)
        count += 1
        if count % 100 == 0:
            print 'Processed %d out of %d' % (count, total)
            pickle_save(CENSUS_DATA_CACHE, path.join(CACHE_DIR, 'census_data_cache'))
            pickle_save(BLOCK_DATA_CACHE, path.join(CACHE_DIR, 'block_data'))
    
    writer.save(path.join(LATLNGS_SHP_DIR, str(cityid) + '_age'))
    

if __name__ == '__main__':
    compute_city(153)