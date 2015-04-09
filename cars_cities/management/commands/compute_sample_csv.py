import csv
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings

from ...constants import GEO_DB
from ...utils.files import ensure_dirs


class Command(BaseCommand):
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Querying for sample data...')
        cursor = connections[GEO_DB].cursor()
        cursor.execute('SELECT cityid, lat, lng FROM samples WHERE sampled=1')
        raw_data = cursor.fetchall()
        cursor.close()
        self.stdout.write('Finished querying for sample data!')
        
        data = defaultdict(set)
        for cityid, lat, lng in raw_data:
            data[cityid].add((lat, lng))
        
        for cityid in data:
            self.stdout.write('Writing csv for city %s...' % cityid)
            filename = settings.SAMPLES_DIR + '/%s.csv' % cityid
            ensure_dirs(filename)
            with open(filename, 'wb') as csvfile:
                writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                for item in data[cityid]:
                    writer.writerow(item)
                    