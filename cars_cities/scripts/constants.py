import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
ARCGIS_DIR = os.path.join(CACHE_DIR, 'arcgis')
SAMPLES_DIR = os.path.join(CACHE_DIR, 'samples')
SHAPEFILE_DIR = os.path.join(SAMPLES_DIR, 'shp')
STATS_DIR = os.path.join(CACHE_DIR, 'stats')
CITY_DIR = os.path.join(CACHE_DIR, 'city')
CITY_BOUNDARY_SHP_DIR = os.path.join(CACHE_DIR, 'city_boundary_shp')
GROUPS_DIR = os.path.join(CITY_DIR, 'groups')
LATLNGS_DIR = os.path.join(CITY_DIR, 'latlngs')
HOTSPOTS_DIR = os.path.join(CITY_DIR, 'hotspots')
LATLNGS_SHP_DIR = os.path.join(LATLNGS_DIR, 'shp')
CONVEXHULL_DIR = os.path.join(SAMPLES_DIR, 'convexhull')
RESAMPLE_DIR = os.path.join(CACHE_DIR, 'resample')
DOWNSAMPLE_DIR = os.path.join(CACHE_DIR, 'downsample')

CITY_IDS = [int(f.split('.')[0]) for f in os.listdir(SAMPLES_DIR) if f.endswith('.csv')]

PROJECTION_FILE = os.path.join(ARCGIS_DIR, 'WGS 1984.prj')

MAKES = [
'nissan',
'mitsubishi',
'mercury',
'mercedes-benz',
'mclaren',
'mazda',
'maybach',
'maserati',
'mini',
'lotus',
'lincoln',
'lexus',
'land rover',
'lamborghini',
'kia',
'jeep',
'jaguar',
'isuzu',
'infiniti',
'hyundai',
'honda',
'hummer',
'geo',
'gmc',
'ford',
'fisker',
'ferrari',
'fiat',
'eagle',
'dodge',
'daewoo',
'chrysler',
'plymouth',
'chevrolet',
'cadillac',
'buick',
'bugatti',
'bentley',
'bmw',
'audi',
'aston martin',
'acura',
'am general',
'oldsmobile',
'panoz',
'pontiac',
'porsche',
'ram',
'rolls-royce',
'saab',
'saturn',
'scion',
'spyker',
'subaru',
'suzuki',
'tesla',
'toyota',
'volkswagen',
'volvo',
'smart'
]