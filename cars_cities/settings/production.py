from _base import *


for name, db in DATABASES.iteritems():
    if db.get('HOST'):
        db['HOST'] = 'localhost'

STATIC_URL = '/static/'
DEBUG = True
