import csv
from shutil import copyfile
from os.path import join, exists

import shapefile
from constants import RESAMPLE_DIR, CITY_IDS


def shp_to_csv(filename, city_id):
    """
    Converts sampling CSV (lat, long) into shapefiles
    """
    print 'Processing shapefile %s...' % filename
    reader = shapefile.Reader(filename)
    writer = csv.writer(open(filename + '.csv', 'wb+'), delimiter=',',
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)

    count = 0
    for shape in reader.shapes():
        writer.writerow(shape.points[0])
        count += 1
        if count % 10000 == 0:
            print 'Written %s rows' % count

    print 'FINISHED'

if __name__ == '__main__':
    for city_id in CITY_IDS:
        target_file = 'C:\\Users\\huifang\\Desktop\\Dropbox\\Stanford\\Research\\cvpr2015\\resample\\%s.csv' % city_id
        if exists(target_file):
            print 'City %s csv already exists, continuing' % city_id
            continue
        city_id = str(city_id)
        try:
            shp_to_csv(join(RESAMPLE_DIR, city_id, 'sample_grid_clipped'), city_id)
        except Exception as e:
            print 'ERROR', str(e)
            continue
        copyfile(join(RESAMPLE_DIR, city_id, 'sample_grid_clipped.csv'), target_file)
