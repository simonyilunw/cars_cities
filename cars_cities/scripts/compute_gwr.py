from os import path
import sys

try:
    import arcpy
except ImportError:
    print 'Cannot import arcpy. Abort.'
    sys.exit(1)
    
from constants import LATLNGS_SHP_DIR, CACHE_DIR, PROJECTION_FILE

AREA_COMPUTE_EXPRESSION = '{0}'.format('!SHAPE.area@SQUAREMILES!')  


def compute_gwr(cityid):
    input_path = path.join(LATLNGS_SHP_DIR, '%s_age.shp' % cityid)
    output_path = path.join(CACHE_DIR, 'gwr', '%s.shp' % cityid)
    rasters_path = path.join(CACHE_DIR, 'gwr_rasters')
    print 'Computing gwr for city %s' % cityid
    arcpy.GeographicallyWeightedRegression_stats(input_path, 'income', 'price', output_path, 
                                                 'ADAPTIVE', 'BANDWIDTH PARAMETER',
                                                 '#', '25', '#', rasters_path,)
    print 'DONE!'


if __name__=='__main__':
    compute_gwr(153)
        