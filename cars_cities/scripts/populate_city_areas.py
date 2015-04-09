from os import path
import sys
import us

import cPickle as pickle

from constants import STATS_DIR, CITY_IDS, CITY_DIR, GROUPS_DIR
from cars_cities.models import City


with open(path.join(STATS_DIR, 'city_areas.txt')) as f:
    lines = f.readlines()

data = []
for line in lines:
    line = filter(lambda s: s, line.strip().split('   '))
    
    line[0] = line[0].replace('City', '').replace('city,', '').replace('town', '')
    line[0] = line[0].replace('(balance),', '').replace('CDP', '').replace(',','')
    line[0] = line[0].replace('-Richmond County', '').replace('St.', 'saint')
    line[0] = line[0].replace('-Davidson', '').replace('St.', 'saint')
    line[0] = line[0].strip().lower()
    line[1] = line[1].replace(',', '')
    
    city = ' '.join(line[0].split(' ')[:-1])
    state = line[0].split(' ')[-1]
    
    data.append([city, state, float(line[1])])
    
for cityid in CITY_IDS:
    city = City(str(cityid))
    #print 'Processing %s, %s' % (city.name, city.state)
    
    name = city.name.replace('city', '').replace('st.', 'saint').lower().strip()
    state = us.states.lookup(city.state).abbr.lower()
    for d in data:
        if d[0].lower().strip() == name and d[1] == state:
            print 'MATCHED', city.name, city.state
            city.area = d[2]
            city.save_state()
            break
    else:
        print 'DID NOT MATCH', city.name, city.state
