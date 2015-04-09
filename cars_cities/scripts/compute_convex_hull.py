from os import path
import sys

try:
    import arcpy
except ImportError:
    print 'Cannot import arcpy. Abort.'
    sys.exit(1)
    
from constants import SHAPEFILE_DIR, CONVEXHULL_DIR, CITY_IDS, PROJECTION_FILE

AREA_COMPUTE_EXPRESSION = '{0}'.format('!SHAPE.area@SQUAREMILES!')  


def compute_convex_hull(cityid):
    input_path = path.join(SHAPEFILE_DIR, '%s.shp' % cityid)
    output_path = path.join(CONVEXHULL_DIR, '%s.shp' % cityid)
    
    print 'Computing convex hull for city %s' % cityid
    arcpy.MinimumBoundingGeometry_management(input_path, output_path, 'CONVEX_HULL', 'ALL')
    arcpy.DefineProjection_management(output_path, PROJECTION_FILE)
    
    arcpy.AddField_management(output_path, 'area', 'Double')
    arcpy.CalculateField_management(output_path, 'area', AREA_COMPUTE_EXPRESSION, 'PYTHON', )
    print 'DONE!'


if __name__=='__main__':
    for cityid in CITY_IDS:
        compute_convex_hull(cityid)
        