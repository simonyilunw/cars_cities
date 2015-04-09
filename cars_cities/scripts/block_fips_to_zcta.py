import csv
from os import listdir

from shutil import copyfile
from os.path import join, exists

import shapefile
from constants import CACHE_DIR, RESAMPLE_DIR, CITY_IDS


def shp_to_csv(filename, city_id):
    """
    Converts sampling CSV (lat, long) into shapefiles
    """
    print 'Processing shapefile %s...' % filename
    reader = shapefile.Reader(filename)

    count = 0
    for shape in reader.shapes():
        writer.writerow(shape.points[0])
        count += 1
        if count % 10000 == 0:
            print 'Written %s rows' % count

    print 'FINISHED'

if __name__ == '__main__':
    filename = join(CACHE_DIR, 'block_fips_to_zcta.csv')
    writer = csv.writer(open(filename + '.csv', 'wb+'), delimiter=',',
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)

    for f in listdir('D:\\topological_faces'):
        if f.endswith('.shp'):
            reader = shapefile.Reader('D:\\topological_faces\\' + f)
            print f
            for record in reader.records():
                state = record[1]
                county = record[2]
                tract = record[3]
                block = record[5]
                zcta5 = record[7]
                writer.writerow([state, county, tract, block, zcta5])
            print 'done'
