from math import radians, cos, sin, asin, sqrt
import math, time
import numpy as np
import scipy.optimize as optimize
from osgeo import osr, gdal
import random
from random import shuffle
from get_data import getAllObservation, getTempOfAAtationADay, getTerraObsPairs,getSateliteADay, moiseture_getTerraObsPairs
from operator import itemgetter, attrgetter
from scipy import interpolate
from scipy.interpolate import griddata
import matplotlib
import matplotlib.pyplot as plt
from setting import *
import datetime, time
from dateutil.relativedelta import relativedelta

def convertTimeEpochToNormal(EpochSeconds):
	now = datetime.datetime.fromtimestamp(EpochSeconds)
	now = now - datetime.timedelta(hours=7) 
	now = now + relativedelta(years=23)
	#print now.month
	#print now.year
	#print now.day
	#print now.time
	#print now.ctime()
	return now

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    #print 'from ', lat1, ' ', lon1, ' to ', lat2, ' ', lon2
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    #lon1, lat1, lon2, lat2 = map(radians, [lat1, lon1, lat2, lon2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # 6367 km is the radius of the Earth
    km = 6367 * c
    return km

def distance(lat1, lon1, lat2, lon2):
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return d
def covariance(x, y):
	size = len(x)
	meanx = sum(x)/size
	meany = sum(y)/size
	cov = 0
	for i in xrange(0,size):
		cov = cov + (x[i]-meanx)*(y[i]-meany)
	cov = cov/(size-1)
	#print x
	#print cov
	#time.sleep(1)
	return cov
def semivariance(x, y):
	#print x
	#print y 
	size = len(x)
	semi = 0
	for i in xrange(0,size):
		semi = semi + (x[i] - y[i])*(x[i] - y[i])
	semi = semi/(2*size)
	#print 'n=', size, 'semi=',semi 
	#time.sleep(1)
	return semi
#Optimize c0, a0 for fitting model
#SELECT gid
#FROM vnm_adm1
#WHERE ST_Contains(geom, ST_SetSRID(ST_Point(105.1043443253471, 21.3150676015829),4326))
#Optimize the fitting function with type fct
#x: list of distance
#y: list of semi value 
def opt( fct, x, y, parameterRange=None, meshSize=1000 ):
    #Initialize range
    sill = 0.95*max(y)
    if parameterRange == None:
        parameterRange = [ x[1], x[-1] ]
	#Initialize mse array    
    mse = np.zeros( meshSize )
	#create a list of uniform distribution from min to max
    a = np.linspace( parameterRange[0], parameterRange[1], meshSize )
    #Try each a[i]
    for i in range( meshSize ):
    	for j in xrange(len(y)):
	    mse[i] = mse[i] + ( y[j] - spherical( x[j], a[i] ,sill) )**2.0
	mse[i] = mse[i]/len(y)
    #mse[i] = np.mean( ( y - spherical( x, a[i] ,sill) )**2.0 )
    #print 'MIN MSE inside opt =', min(mse)
    return a[ mse.argmin() ], sill, min(mse)
#SPERICAL 
#a0: The hien do nghieng cua ham spherical
#c0: Sill value ~95% max semi value
def spherical(h, a0, c0):
	if h > a0:
		return c0
	else:
		item = h/a0
		return c0*(1.5*item-0.5*(item**3))
def genFitting(h, y, level):
	'''
	return f, mse
	'''
	#FIT ham bac 2
	z = np.poly1d(np.polyfit(h, y, level))
	mse = 0
	for i in xrange(len(y)):
		mse = mse+ ( y[i] - z(h[i]))**2.0
	print 'Ham bac ', level, ': ', z, 'mse= ', mse
	return z, mse
def semiToCov(h, a0, c0):
	return c0 - spherical(h, a0, c0)
def func(data, a, b, c):
    return a*data[:,0]+ b*data[:,1] + c
#http://stackoverflow.com/questions/15413217/fitting-3d-points-python    
def curveFitting(A):
	#A[:,2] = func(A[:,:2], 100.5,3,4)
	#print A
	guess = (1,1,1)
	A = np.asarray(A)
	guess = (1,1,1)
	params, pcov = optimize.curve_fit(func, A[:,:2], A[:,2], guess)
	#print(params)
	return params
def inverseMatrix(X):
	Y = np.zeros([X.shape[1],X.shape[0]])
	for i in range(X.shape[0]):
		for j in range(X.shape[1]):
			Y[j][i] = X[i][j]
	#print X
	#print Y
	return Y
def exportGeotiff(filename, raster, row, col, resolution, minLon, minLat):
	format = "GTiff"
	driver = gdal.GetDriverByName( format )
	#dst_ds = driver.Create(filename, col, row, 1, gdal.GDT_Byte )
	dst_ds = driver.Create(filename, col, row, 1, gdal.GDT_Float32 )
	# top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
	dst_ds.SetGeoTransform( [ minLon, resolution, 0, minLat, 0, resolution ] )
	# set the reference info 
	srs = osr.SpatialReference()
	srs.SetWellKnownGeogCS("WGS84")
	dst_ds.SetProjection( srs.ExportToWkt() )
	dst_ds.GetRasterBand(1).WriteArray(raster)
def resampling(Z):
	H = np.zeros_like( Z )
	minH = abs(Z).min()
	maxH = abs(Z).max()
	delta = maxH -minH
	for i in range( Z.shape[0] ):
	    for j in range( Z.shape[1] ):
	        H[i,j] = np.round( (255*(Z[i,j] - minH))/delta )
	return H
#Resampling: 1->5
def resampling_5(Z):
	H = np.zeros_like( Z )
	minH = abs(Z).min()
	maxH = abs(Z).max()
	delta = maxH -minH
	for i in range( Z.shape[0] ):
	    for j in range( Z.shape[1] ):
	        H[i,j] = 1+ np.round( (4*(Z[i,j] - minH))/delta )
	return H
def getTrendValue(curve, lat, lon):
	#curve: z = ax + by + c
	return curve[0]*lat + curve[1]*lon + curve[2]
def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]
#Reindex a list with new id: from 0 -> len()
def reIndex(list_train):
	new_list = []
	size = len(list_train)
	for i in xrange(0,size):
		item = list_train[i]
		new_item = [ i +1 ,item[1], item[2], item[0], item[4]] #fake id, lat, lon, real_id, alt
		new_list.append(new_item)
	return new_list
#hmm, slice, not slide :|
def slide(fold, list_all):
	#Contain fold (trainng/test) SET
	global_data = {}
	shuffle(list_all)
	#print str(math.ceil( len(list_all)/fold))
	size_fold = int(math.ceil( len(list_all)/fold))
	data = list(chunks(list_all, size_fold))
	for i in xrange(0,fold):
		list_test = data[i]
		list_train = list_all[:]#Copy all to train
		for x in list_test:#remove test from train
			list_train.remove(x)
		list_test = sorted(list_test, key=itemgetter(0))
		list_train = sorted(list_train, key=itemgetter(0))
		list_train = reIndex(list_train)
		item = [list_test, list_train]
		global_data[i] = item
		#print global_data[i][0]
		#print global_data[i][1]
	return global_data
def calculateSE(result,result_kri_backup, list_all_test, minLat, minLon, shift, date_to, f,sate_lite_value, f_se):
	f.write('calculateSE\n')
	for item in list_all_test:
		print item
	se = 0
	se_sate = 0 
	sate_count = 0
	list_test_temp = []
	for item in list_all_test:
		#item: id, lat, lon
		#test: id, lat, lon, alt, temp13
		test = getTempOfAAtationADay(item[0], date_to)
		temp = test[4]
		lat = test[1]
		lon = test[2]
		alt = test[3]
		#normalize temp by alt
		temp = temp + 0.64*(alt/100) #for normalize by alt
		list_test_temp.append(test)
		i = int(round((lat - minLat)/shift))
		j = int(round((lon - minLon)/shift))
		krige_temp = result[i][j]
		#print i, j, temp,  krige_temp
		se = se + (temp - krige_temp)**2
		f.write(str(i)+ ' '+str(j)+ ' ' + str(temp)+ ' ' + str(krige_temp)+ ': ' + str(se) + '\n')
		#print se
		if sate_lite_value[i][j] != 0:
			sate_count = sate_count + 1
			se_sate = se_sate + (temp - krige_temp)**2
			print 'temp: ', temp, ' krige_temp: ', krige_temp
			print 'se_sate ', sate_count, str(se_sate/sate_count)
			f_se.write(str(item[0]) +':'+str(i) + ':' +str(j) +':' +str(temp) +":" + str(krige_temp)+":" + str((temp-krige_temp)**2)+":" + str(sate_lite_value[i][j]) +':'+ str(result_kri_backup[i][j]) +'\n') 
	if sate_count != 0:
		f.write( str(se/len(list_all_test)) +" " + str(se_sate/sate_count) + '\n')
		return se/len(list_all_test), se_sate, sate_count
	else:
		f.write( str(se/len(list_all_test)) +  ' 0 \n')
		return se/len(list_all_test), 0, 0
#http://www.onthesnow.com/news/a/15157/ask-a-weatherman--how-does-elevation-affect-temperature-
def removeResidualTempByAlt(item):
	#item: id(0), lat(1), lon(2), alt(3), temp(4)
	item[4] = item[4] + 0.64*(item[3]/100)
#Return: list of all (Terra-Obs) pairs; z(ax+b); mse
def calSateliteObsRelation():
	#list of item[id, terra_temp, obs_temp, terra_date, terra_time]
	list = getTerraObsPairs()
	list_all = zip(*list)
	list_satelite = list_all[1]
	list_obs = list_all[2]
	#Fit obs = a*sate+b
	z, mse_level_1 = genFitting(list_satelite, list_obs, 1)	
	correlation = np.corrcoef(list_satelite, list_obs)[0,1]
	print 'calSateliteObsRelation: ', z, mse_level_1, correlation
	return list, z, mse_level_1
def standardDerivation(list):
	print 'derivation ', len(list)
	for item in list:
		print item
		if item > 10:
			time.sleep(1)
	print np.mean(list)
	return 0
def calErrorMap():
	#Init
	max_id = 97# 97 tram
	list_all = []
	for x in xrange(0, max_id):
		#print x
		list_all.append([])
	#Get (S1-Obs)
	list, z, mse_level_1 = calSateliteObsRelation()
	list_se = []
	# S1->S2
	for item in list:
		if date_to in str(item[3]):
			print 'id',str(item[0]), item[1],'->', z(item[1]), item[2],abs(z(item[1])-item[2])
		item[1] = z(item[1])
		#Thong ke abs(S2-Obs)
		#print abs(item[1]-item[2])
		list_all[item[0]-1].append(abs(item[1]-item[2]))
		list_se.append((abs(item[1]-item[2]))**2)
	#Tinh varriance(S2-Obs)
	print 'Satellite SE: ',sum(list_se)/len(list_se)
	#time.sleep(10)
	list_derivation = []
	for item in list_all:
		#print item
		standard_deviation = np.std(item)
		#standardDerivation(item)
		list_derivation.append(standard_deviation)
		#print standard_deviation
	deri_avg = sum(list_derivation)/len(list_derivation)
	list_all_station = getAllObservation()
	list_id_lat_lon_deri = []
	for item in list_all_station:
		#print list_derivation[item[0]-1]
		#id, lat, lon, deri
		new_item = [item[0], item[1], item[2], list_derivation[item[0]-1]]
		if new_item[3] > 2.5:
			print new_item
		list_id_lat_lon_deri.append(new_item)
	return list_id_lat_lon_deri, deri_avg, z
#http://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html#scipy.interpolate.griddata	
def interpolate(list, row, col, shift, minLon, minLat, avg):
	print 'interpolate'
	points = np.random.rand(len(list) + 4, 2)
	list_values = []
	for i in xrange(0,len(list)):
		item = list[i]
		#print minLat, item[1]
		#print minLon, item[2]
		points[i][0] = int(round(10*(item[1]-minLat)))
		points[i][1] = int(round(10*(item[2]-minLon)))
		list_values.append(item[3])
	list_values.append(avg)
	list_values.append(avg)
	list_values.append(avg)
	list_values.append(avg)
	size = len(list)
	points[size][0] = 0
	points[size][1] = 0
	points[size+1][0] = 0
	points[size+1][1] = col -1
	points[size+2][0] = row-1
	points[size+2][1] = 0
	points[size+3][0] = row-1
	points[size+3][1] = col-1

	#print points
	#for item in list:
		#point_item = (int(round(10*(item[1]-minLat))), int(round(10*(item[2]-minLat))))
		#list_points_x.append(int(round(10*(item[1]-minLat)))
		#list_points_y.append(int(round(10*(item[2]-minLat)))
	#	list_values.append(item[3])
	#list_all = zip(*list)
	#list_id = list_all[0]
	#list_lat = list_all[1]
	#list_lon = list_all[2]
	#list_deri = list_all[3]
	grid_x, grid_y = np.mgrid[0:row, 0:col]
	grid_z1 = griddata(points, list_values, (grid_x, grid_y), method='linear')#nearest,cubic
	plt.plot( points[:,1],points[:,0], 'k.', ms=1)
	plt.imshow(grid_z1,  origin='lower')
	plt.colorbar()
	plt.title('Linear')
	if LOG:
		plt.show()
	return grid_z1
def getSateliteDeriMap():
	list, avg, z = calErrorMap()
	grid_satelite_deri = interpolate(list, row, col, shift, minLon, minLat, avg)
	return grid_satelite_deri, z
#input: kriging_value, kriging_deri, sate_value, sate_deri
def assimilate(kri_value, kri_deri, sate_value, sate_deri, f_da):
	print 'assimilating: ', kri_value, kri_deri, sate_value, sate_deri
	assimilated = (kri_value*sate_deri + sate_value*kri_deri)/(kri_deri + sate_deri)
	print assimilated
	f_da.write(str(kri_value)+':' +str(kri_deri)+':'+ str(sate_value)+':'+ str(sate_deri) +':'+ str(assimilated) +'\n')
	return (kri_value*sate_deri + sate_value*kri_deri)/(kri_deri + sate_deri)
def get_sate_lite_value(date, z_sate_to_surface):
	sate_lite_value = np.zeros([row,col])
	#Get all satelite data of date, then fill the matrix
	list = getSateliteADay(date)
	# station_id, lat, lon, alt, temp, humid, rain 
	for item in list:
		#print item
		lat = item[1]
		lon = item[2]
		alt = item[3]
		temp = item[4]
		#minLat + i*shift,minLon + j*shift
		i = int(round((lat-minLat)/shift))
		j = int(round((lon-minLon)/shift))
		sate_lite_value[i][j] = z_sate_to_surface(temp) + 0.64*(alt/100) #for normalize by alt
		print '(' +str(i), str(j) + ')','id', item[0],temp,z_sate_to_surface(temp), sate_lite_value[i][j]
	return sate_lite_value

##FOR MOISETURE
def moiseture_get_sate_lite_value(date, z_sate_to_surface):
	sate_lite_value = np.zeros([row,col])
	#Get all satelite data of date, then fill the matrix
	list = getSateliteADay(date)
	# station_id, lat, lon, alt, temp, humid, rain 
	for item in list:
		#print item
		lat = item[1]
		lon = item[2]
		alt = item[3]
		#temp = item[4]
		humid = item[5]
		#minLat + i*shift,minLon + j*shift
		i = int(round((lat-minLat)/shift))
		j = int(round((lon-minLon)/shift))
		sate_lite_value[i][j] = z_sate_to_surface(humid)
		print '(' +str(i), str(j) + ')','id', item[0],humid,z_sate_to_surface(humid), sate_lite_value[i][j]
	return sate_lite_value
def moiseture_calErrorMap():
	#Init
	max_id = 97# 97 tram
	list_all = []
	for x in xrange(0, max_id):
		#print x
		list_all.append([])
	#Get (S1-Obs)
	list, z, mse_level_1 = moisture_calSateliteObsRelation()
	list_se = []
	# S1->S2
	for item in list:
		if date_to in str(item[3]):
			print 'id',str(item[0]), item[1],'->', z(item[1]), item[2],abs(z(item[1])-item[2])
		item[1] = z(item[1])
		#Thong ke abs(S2-Obs)
		#print abs(item[1]-item[2])
		list_all[item[0]-1].append(abs(item[1]-item[2]))
		list_se.append((abs(item[1]-item[2]))**2)
	#Tinh varriance(S2-Obs)
	print 'Satellite SE: ',sum(list_se)/len(list_se)
	#time.sleep(10)
	list_derivation = []
	for item in list_all:
		#print item
		standard_deviation = np.std(item)
		#standardDerivation(item)
		list_derivation.append(standard_deviation)
		#print standard_deviation
	deri_avg = sum(list_derivation)/len(list_derivation)
	list_all_station = getAllObservation()
	list_id_lat_lon_deri = []
	for item in list_all_station:
		#print list_derivation[item[0]-1]
		#id, lat, lon, deri
		new_item = [item[0], item[1], item[2], list_derivation[item[0]-1]]
		if new_item[3] > 2.5:
			print new_item
		list_id_lat_lon_deri.append(new_item)
	return list_id_lat_lon_deri, deri_avg, z
def moisture_calSateliteObsRelation():
	#list of item[id, terra_humid, obs_humid, terra_date, terra_time]
	list = moiseture_getTerraObsPairs()
	list_all = zip(*list)
	list_satelite = list_all[1]
	list_obs = list_all[2]
	#Fit obs = a*sate+b
	z, mse_level_1 = genFitting(list_satelite, list_obs, 1)	
	correlation = np.corrcoef(list_satelite, list_obs)[0,1]
	print 'calSateliteObsRelation: ', z, mse_level_1, correlation
	return list, z, mse_level_1
def moiseture_getSateliteDeriMap():
	list, avg, z = moiseture_calErrorMap()
	grid_satelite_deri = interpolate(list, row, col, shift, minLon, minLat, avg)
	return grid_satelite_deri, z

#TEST
#A = np.array([(19,20,24), (10,40,28), (10,50,31)])
#calSateliteObsRelation()

#getSateliteDeriMap()

'''
A = []
for x in xrange(1,10):
	item = (x, x+1, x+2)
	A.append(item)
A = np.asarray(A)
curveFitting(A)
minLat = 8.4
maxLat = 23.6
minLon = 102.1
maxLon = 109.8
shift = 0.1
row = int((maxLat-minLat)/shift)
col = int((maxLon-minLon)/shift)
raster = np.zeros( (row, col) )
for x in xrange(10,20):
	for y in xrange(10,20):
		raster[x][y] = 100
exportGeotiff('filename', raster, row, col, shift, minLon, minLat)

#list_all = range(0,10)
list_all = getAllObservation()
#list_all = list_all[:10]
result = slide(10, list_all)
print result[0][0]
#print global_data[i][1]
'''
