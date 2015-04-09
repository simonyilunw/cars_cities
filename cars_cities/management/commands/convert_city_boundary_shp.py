from os import path

from django.core.management.base import BaseCommand
from django.conf import settings

import us
import shapefile

from ...models import City


class Command(BaseCommand):
    """
    Converts city boundary shp data obtained from the census website into list of [x,y] and store 
    in City data files under the attribute "boundary"
    """
    def handle(self, *args, **kwargs):
        cities = [City(cityid) for cityid in settings.CITY_IDS]
        
        self.stdout.write('Loaded %d city data files' % len(cities))
        
        city_dict = {(city.name.strip().lower(), city.state.strip().lower()): city for city in cities}
        
        for state in us.STATES:
            try:
                reader = shapefile.Reader(path.join(settings.CACHE_DIR, 'city_boundary_shp', 
                                                    'tl_2014_%s_place' % state.fips))
            except shapefile.ShapefileException:
                self.stderr.write('State %s places SHP file not found' % state.name)
                continue
            else:
                self.stdout.write('Processing SHP file for %s' % state.name)
                
            shaperecords = reader.shapeRecords()
            for shaperecord in shaperecords:
                record = shaperecord.record
                shape = shaperecord.shape
                name = record[4]
                
                match_criteria = (name.lower(), state.name.lower())
                matched_city = city_dict.get(match_criteria)
                if matched_city:
                    self.stdout.write('Match criteria: %s' % str(match_criteria))
                    self.stdout.write('Matched boundary for cityid %s' % matched_city.city_id)
                    
                    matched_city.boundary = shape.points
                    matched_city.save_state()
        
        cities_without_boundary = [city.name for city in cities if not hasattr(city, 'boundary')]
        self.stderr.write('Cities without boundaries: %s' % cities_without_boundary)
        
                