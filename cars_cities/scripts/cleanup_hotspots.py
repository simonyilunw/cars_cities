import os, sys

import shapefile

from constants import HOTSPOTS_DIR, CITY_IDS


CITY_IDS_CUSTOM = {113}


def cleanup_hotspots(city_id):
    print 'Cleaning up hotspots for', city_id
    reader = shapefile.Reader(os.path.join(HOTSPOTS_DIR, str(city_id) + '_hotspots.shp'))
    hotspots = shapefile.Editor(shapefile=os.path.join(HOTSPOTS_DIR, str(city_id) + '_hotspots.shp'))
    
    print reader.fields
    num_deleted = 0
    for index, sr in enumerate(reader.shapeRecords()):
        if float(sr.record[1]) <= 0:
            print 'Deleting %d' % index
            try:
                hotspots.delete(index - num_deleted)
            except IndexError:
                print 'Cannot delete %d due to IndexError' % index
            else:
                num_deleted += 1
        else:
            print float(sr.record[2])
    
    #hotspots.save(os.path.join(HOTSPOTS_DIR, str(city_id) + '_cleaned.shp'))
    print 'FINISHED %s!' % city_id


if __name__ == '__main__':
    for cityid in CITY_IDS_CUSTOM or CITY_IDS:
        try:
            cleanup_hotspots(cityid)
        except Exception as e:
            print 'Cannot cleanup hotspot for %s: %s' % (cityid, str(e))
