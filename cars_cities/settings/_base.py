"""
Django settings for cars_cities project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from ..constants import ALL_CARS_DB, BOSTON_CARS_DB, GEO_DB, GEOCARS_DB, GEOCARS_CRAWLED_DB

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
CITY_DIR = os.path.join(CACHE_DIR, 'city')
GROUPS_DIR = os.path.join(CITY_DIR, 'groups')
LATLNGS_DIR = os.path.join(CITY_DIR, 'latlngs')
LATLNGS_SHP_DIR = os.path.join(LATLNGS_DIR, 'shp')
HOTSPOTS_DIR = os.path.join(CITY_DIR, 'hotspots')
STATS_DIR = os.path.join(CACHE_DIR, 'stats')
SAMPLES_DIR = os.path.join(CACHE_DIR, 'samples')
SHAPEFILE_DIR = os.path.join(SAMPLES_DIR, 'shp')
CONVEXHULL_DIR = os.path.join(SAMPLES_DIR, 'convexhull')
POLYGONS_DIR = os.path.join(SAMPLES_DIR, 'polygons')
MA_DATA_DIR = os.path.join(CACHE_DIR, 'ma_data/Spatial')
CITY_IDS = [int(f.split('.')[0]) for f in os.listdir(SAMPLES_DIR) if f.endswith('.csv')]

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$6q)qsk%fqhse#kaghsqxwu4(z$8y!)!nfpe#b13qtx@wywz1)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cars_cities'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'cars_cities.urls'

WSGI_APPLICATION = 'cars_cities.wsgi.application'


# Database
DATABASE_TEMPLATE = {
    'ENGINE': 'django.db.backends.mysql',
    'HOST': 'imagenet.stanford.edu',
    'USER': 'duchen',
    'PASSWORD': '', # TODO add a password this this account for security!
    'PORT': '3306',   
}

DATABASE_NAMES = (ALL_CARS_DB, BOSTON_CARS_DB, GEO_DB, GEOCARS_DB, GEOCARS_CRAWLED_DB)

DATABASES = {}
for name in DATABASE_NAMES:
    template = DATABASE_TEMPLATE.copy()
    template['NAME'] = name
    DATABASES[name] = template
    
# add a default DB (some random sqlite db since we won't ever really need to use this db)
DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
