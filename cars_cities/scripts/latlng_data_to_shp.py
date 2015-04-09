import sys
import csv
from os import path

try:
    import arcpy
except ImportError:
    print 'Cannot import arcpy. Will not adjust projections.'
    projection = False
else:
    projection = True

import shapefile
from constants import CITY_IDS, LATLNGS_DIR, LATLNGS_SHP_DIR, PROJECTION_FILE, MAKES

from utils import pickle_load

override = True

CUSTOM_CITIES = {}


def latlng_to_shp(cityid):
    """
    Converts sampling CSV (lat, long) into shapefiles
    """
    if not override and path.isfile(path.join(LATLNGS_SHP_DIR, str(cityid) + '.shp')):
        print '%s.shp already exists. Skipping' % cityid
        return

    print 'Processing latlng data for city %s...' % cityid
    data = pickle_load(path.join(LATLNGS_DIR, str(cityid)))
    print 'Data loaded'

    writer = shapefile.Writer(shapefile.POINT)
    writer.autoBalance = 1
    writer.field('price', 'N')

    for make in MAKES:
        writer.field(make[:10], 'N', 19, 9)

    count = 0
    for (lat, lng) in data:
        writer.point(lng, lat)

        record = {
            'price': data[(lat, lng)]['price']
        }
        for make in MAKES:
            if 'makes' in data[(lat, lng)]:
                record[make[:10]] = str(data[(lat, lng)]['makes'].get(make, 0.0))[:19]
            else:
                record[make[:10]] = 0.0
        writer.record(**record)
        count += 1
        if (count % 5000) == 0:
            print '%s entries copied' % count

    shp_path = path.join(LATLNGS_SHP_DIR, str(cityid))

    print 'Writing shapefile...'
    writer.save(shp_path)
    print 'Defining projection...'
    if projection: arcpy.DefineProjection_management(shp_path + '.shp', PROJECTION_FILE)
    print 'Written shapefile to %s' % shp_path


if __name__ == '__main__':
    for cityid in CUSTOM_CITIES or CITY_IDS:
        try:
            latlng_to_shp(cityid)
        except Exception as e:
            print 'Cannot process', cityid, str(e)
            raise
