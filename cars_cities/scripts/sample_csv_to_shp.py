import csv
from os import path

import shapefile
from constants import CITY_IDS, SAMPLES_DIR, SHAPEFILE_DIR

def csv_to_ship(cityid):
    """
    Converts sampling CSV (lat, long) into shapefiles 
    """
    with open(path.join(SAMPLES_DIR, '%s.csv' % cityid), 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        print 'Processing shapefile %s...' % cityid
        
        writer = shapefile.Writer(shapefile.POINT)
        writer.autoBalance = 1
        writer.field('lat')
        writer.field('lng')
        
        index = 0
        for row in reader:
            lat, lng = map(float, row)
            writer.point(lng, lat)
            writer.record(lng, lat)
            index += 1
            
        shp_path = path.join(SHAPEFILE_DIR, str(cityid))
        writer.save(shp_path)
        print 'Written shapefile to %s' % shp_path


if __name__=='__main__':
    for cityid in CITY_IDS:
        csv_to_ship(cityid)
