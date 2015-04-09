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

from constants import LATLNGS_SHP_DIR, HOTSPOTS_DIR, CITY_IDS

# Houston 197
# Reno 283
# Seattle 205
# SF 293

CITY_IDS_CUSTOM = {}


def compute_hotspots(city_id):
    print 'Computing hotspots for', city_id
    shpfile = os.path.join(LATLNGS_SHP_DIR, str(city_id) + '.shp')
    output = os.path.join(HOTSPOTS_DIR, str(city_id) + '_hotspots.shp')
    arcpy.OptimizedHotSpotAnalysis_stats(shpfile, output, 'price')
    print 'FINISHED %s!' % city_id


if __name__ == '__main__':
    for cityid in CITY_IDS_CUSTOM or reversed(CITY_IDS):
        try:
            compute_hotspots(cityid)
        except Exception as e:
            print 'Cannot compute hotspot for %s: %s' % (cityid, str(e))
