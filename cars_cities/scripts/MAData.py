import sys
import os
from mysql_yilunw import connect_to_db
from scipy import stats
#from numpy import *

# If the package has been installed correctly, this should work:
import Gnuplot, Gnuplot.funcutils
import cPickle as pickle
import urllib2
from sklearn.linear_model import LogisticRegression
import numpy as np

def get_vars_list():
  vars=open('%s_variables.txt'% 'acs').readlines()
  var_keys=[]
  for v in vars:
    var_keys.append(v.split(',')[0])
  return var_keys

def follow_link(br,link):
   print '......link=%s..................'%link
   tried=0
   connected=False
   html=''
   num_to_try=10
   while not connected:
      try:
        html=br.DownloadURL(link)
        connected = True # if line above fails, this is never executed
      except Exception as e: #catch all exceptions
        print 'Error in follow_link: %s trying again' %e
        tried += 1
        if tried > num_to_try:
          print 'cannot download from link: %s' %link
          return
   return html


cities=['boston','springfield','worcester']
muni_ids=[35,281,348]
city_ids=[153,300,154]

zip_income = []
fp = open("income.csv", "r")
for line in fp:
    lineData = line.split(",")
    zip_income.append(int(lineData[0]))
fp.close()


if not os.path.isfile('cars_data'):
	db_name='geocars' 
	db = connect_to_db(db_name)
	cursor = db.cursor()
	make_query='select group_id, price, mpg_highway, mpg_city, hybrid, electric, country, is_foreign from car_metadata'
	cursor.execute(make_query)
	cursor_data = cursor.fetchall()

	car_basic = {}
	for group_id, price, mpg_highway, mpg_city, hybrid, electric, country, is_foreign in cursor_data:
	    thisID = int(group_id)
	    if price == None:
	        price = 0
	    if mpg_highway == None:
	    	mpg_highway = 0
	    if mpg_city == None:
	    	mpg_city = 0
	    car_basic[thisID] = (int(price), int(mpg_highway), int(mpg_city), int(hybrid), int(electric), country, int(is_foreign))


	db_name='geocars_crawled' 
	db = connect_to_db(db_name)
	cursor = db.cursor()
	make_query='select group_id, submodel, years from control_classes'
	cursor.execute(make_query)
	cursor_data = cursor.fetchall()

	car_extended = {}
	for group_id, submodel, years in cursor_data:
	    thisID = int(group_id)
	    years = years[0:4]
	    if not years[0].isdigit():
	    	years = 0
	    car_extended[thisID] = (submodel, int(years))


	db_name='boston_cars' 
	db = connect_to_db(db_name)
	cursor = db.cursor()




	cars_data = []

	for zip_code in zip_income:
	    if int(zip_code) != 0:
	    	print zip_code

	        make_query='select group_id from ma_detected_cars where zipcode=%d' % int(zip_code)
	        cursor.execute(make_query)
	        cursor_data = cursor.fetchall()

	        thisList = [0.0] * 34
	        for group_id in cursor_data:
	        	group_id = int(group_id[0])
	        	basic = car_basic[group_id]
	        	extended = car_extended[group_id]
	        	thisList[0] += 1
	        	thisList[2] += basic[0]
	        	thisList[4] += basic[1]
	        	thisList[5] += basic[2]
	        	thisList[6] += basic[3]
	        	thisList[7] += basic[4]
	        	if basic[5] == 'germany':
	        		thisList[8] += 1
	        	elif basic[5] == 'usa':
	        		thisList[9] += 1
	        	elif basic[5] == 'south korea':
	        		thisList[10] += 1
	        	elif basic[5] == 'sweden':
	        		thisList[11] += 1
	        	elif basic[5] == 'japan':
	        		thisList[12] += 1
	        	elif basic[5] == 'italy':
	        		thisList[13] += 1
	        	elif basic[5] == 'netherlands':
	        		thisList[14] += 1
	        	elif basic[5] == 'england':
	        		thisList[15] += 1
	        	elif basic[5] == 'france':
	        		thisList[16] += 1
	        	thisList[17] += basic[6]

	        	if extended[0] == 'coupe':
	        		thisList[18] += 1
	        	elif extended[0] == 'minivan':
	        		thisList[19] += 1
	        	elif extended[0] == 'sedan':
	        		thisList[20] += 1
	        	elif extended[0] == 'hatchback':
	        		thisList[21] += 1
	        	elif extended[0] == 'convertible':
	        		thisList[22] += 1
	        	elif extended[0] == 'regular cab':
	        		thisList[23] += 1
	        	elif extended[0] == 'extended cab':
	        		thisList[24] += 1
	        	elif extended[0] == 'crew cab':
	        		thisList[25] += 1
	        	elif extended[0] == 'suv':
	        		thisList[26] += 1
	        	elif extended[0] == 'wagon':
	        		thisList[27] += 1
	        	elif extended[0] == 'van':
	        		thisList[28] += 1

	        	if extended[1] <= 1994 and extended[1] >= 1990:
	        		thisList[29] += 1
	        	elif extended[1] <= 1999:
	        		thisList[30] += 1
	        	elif extended[1] <= 2004:
	        		thisList[31] += 1      	
	        	elif extended[1] <= 2009:
	        		thisList[32] += 1
	        	elif extended[1] >= 2010:
	        		thisList[33] += 1
	        for i in range(2, 34):
	        	if i != 3:
	        		thisList[i] /= thisList[0]
	        if thisList[0] < 100:
	        	print "sdfsdfsdfsdfsdfd %d" % zip_code
	    	cars_data.append(thisList)


	pickle.dump( cars_data, open( "cars_data", "wb" ) )
else:
	cars_data = pickle.load( open( "cars_data", "rb" ) )
        



if not os.path.isfile('census_data'):
	census_data = []

	URL_BASE='http://api.census.gov/data/2012/acs5?key='
	API_KEY='c3f2b964f8b400372d5b511a32860df212775373'
	BASE='%s%s&get='%(URL_BASE,API_KEY)
	vars_list=get_vars_list()
	vars_len = len(vars_list)
	vars=",".join(vars_list)
	
	for zip_code in zip_income:
		thisList = [0.0] * vars_len
		print "census: %d"%zip_code
		query='%s%s&for=zip+code+tabulation+area:%s'%(BASE,vars,zip_code)
		thisLine = urllib2.urlopen(query).read()
		thisData = thisLine.split('\n')[1].replace('[','').replace(']','').split(',')
		for i in range(vars_len):
			if thisData[i] == 'null':
				thisList[i] = 0.0
			else:
				thisList[i] = float(thisData[i][1:-1])

		
		census_data.append( thisList)

		
	pickle.dump( census_data, open( "census_data", "wb" ) )
else:
	census_data = pickle.load( open( "census_data", "rb" ) )




cars_data = np.matrix(cars_data)
census_data = np.matrix(census_data)
lr = LogisticRegression(C=1.0, penalty='l2')
lr.fit(cars_data[0:50,:], np.ravel(census_data[0:50, 11]))
#print lr.score(cars_data[51:72, :], np.ravel(census_data[51:72, 11]))

print cars_data[:, 2]
#print np.ravel(census_data[51:72, 11])
#print lr.predict(cars_data[51:72, :])
'''
total_data = []
our_data = [] 			

for item in cars_data.iteritems():
	zip_code = item[0]
	thisList = item[1]
	if thisList[0] >= 100:
		total_data.append(0)
######################################
		our_data.append(thisList[2])




g = Gnuplot.Gnuplot(debug=1)



####################################
our_data_column = "price"

output_file = our_data_column + ".png"

g.reset()
d = Gnuplot.Data(our_data, total_data)
g('set terminal png')
g('set output \'' + output_file+'\'')
g.title(our_data_column + " corr:" + str(stats.pearsonr(our_data, total_data)[0]))
g.xlabel(our_data_column)
g.ylabel('income')
g.plot(d)
  '''