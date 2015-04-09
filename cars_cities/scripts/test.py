from os import path
import time

from census import Census, ALL
from fcc.census_block_conversions import census_block_dict

import shapefile
from constants import CACHE_DIR, LATLNGS_SHP_DIR
from utils import pickle_load


def compute_city(cityid):
    data = pickle_load(path.join(CACHE_DIR, 'MA_census_data'))
    print data
    
if __name__ == '__main__':
    compute_city(153)