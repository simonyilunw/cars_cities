import os
import sys 

root_path='/imagenetdb/duchen/cars_cities'
path=root_path + '/cars_cities'

if root_path not in sys.path:
    sys.path.append(root_path)
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cars_cities.settings.production")
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
