import os, sys

try:
    print 'Initializing ArcGIS python modules...'
    import arcpy
except ImportError:
    print 'Cannot import arcpy. Abort.'
    sys.exit(1)
else:
    arcpy.env.overwriteOutput = True
    print 'ArcGIS initialization complete'

from constants import LATLNGS_SHP_DIR, CITY_DIR, CITY_IDS, CACHE_DIR
from utils import pickle_save, pickle_load

# Houston 197
# Reno 283
# Seattle 205
# SF 293

CITY_IDS_CUSTOM = {}


def compute_hotspots(city_id):
    print 'Computing Moran index for', city_id
    shpfile = os.path.join(LATLNGS_SHP_DIR, str(city_id) + '.shp')
    moran_index = arcpy.SpatialAutocorrelation_stats(shpfile, 'price', 'NO_REPORT',
                                   'INVERSE_DISTANCE_SQUARED', 'EUCLIDEAN DISTANCE',
                                   'NONE', '100', '#')
    print 'FINISHED %s!' % city_id
    return moran_index


if __name__ == '__main__':
    try:
        moran_indices = pickle_load(os.path.join(CACHE_DIR, 'moran_indices'))
    except Exception as e:
        print 'Error loading moran_indices: %r, creating a new one' % e
        moran_indices = {}

    for cityid in CITY_IDS_CUSTOM or CITY_IDS:
        if cityid in moran_indices:
            print '%s already exists, skipping' % cityid
            continue
        try:
            moran_indices[cityid] = compute_hotspots(cityid).getOutput(0)
        except Exception as e:
            print 'Cannot compute Morans I for %s: %s' % (cityid, str(e))
        else:
            pickle_save(moran_indices, os.path.join(CACHE_DIR, 'moran_indices'))
