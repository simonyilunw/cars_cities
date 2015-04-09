from os import path

from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings

import shapefile

from ...constants import GEO_DB
from ...utils.files import pickle_save


class Command(BaseCommand):
    """
    Converts shp polygons files into list of [x,y] python structs for simpler reading
    """
    def handle(self, *args, **kwargs):
        cursor = connections[GEO_DB].cursor()
        cursor.execute('SELECT cityid, cityname FROM cities')
        city_data_raw = cursor.fetchall()
        cursor.close()
        
        city_data = {}
        for cityid, cityname in city_data_raw:
            city_data[cityid] = cityname.title()
        self.stdout.write('%d cities queried from GEO database' % len(city_data))
        self.stdout.write('%d cities sample csv files found in cache' % len(settings.CITY_IDS))
        
        for cityid in settings.CITY_IDS:
            self.stdout.write('Reading shapefile for %s' % cityid)
            
            shp_path = path.join(settings.CONVEXHULL_DIR, str(cityid))
            reader = shapefile.Reader(shp_path)
            polygon = reader.shapes()[0]
            
            points = [[y, x] for [x, y] in polygon.points] # the long lat are flipped
            center = [0.0, 0.0]
            for point in points:
                center[0] += point[0]
                center[1] += point[1]
            center[0] /= float(len(points))
            center[1] /= float(len(points))
            
            area = float(reader.records()[0][1])
            self.stdout.write('Polygon area is %f sq miles' % area)
            data = {
                'name': city_data.get(cityid, 'unknown city'),
                'center': center,
                'data': points,
                'area': area
            }
            
            pickle_save(data, path.join(settings.POLYGONS_DIR, str(cityid)))
            self.stdout.write('Polygon file saved for %s' % cityid)
        
        self.stdout.write('FINISHED')
