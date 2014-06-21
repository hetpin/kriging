#Simple Kringing Implementation
import numpy as np
import time, os
import matplotlib
import matplotlib.pyplot as plt
from get_data import getTempOfAAtationFromTo,isInVietnam,getAreaIdFromPoint
from get_data import getAllObservation,getAllStaByAreaId, getTempOfAAtationADay
from Utility import haversine, covariance, semivariance, opt,spherical, genFitting, semiToCov, curveFitting,inverseMatrix,exportGeotiff,resampling, resampling_5, getTrendValue
from Utility import slide, calculateSE, removeResidualTempByAlt,getSateliteDeriMap, assimilate, get_sate_lite_value
from Utility import reIndex
from operator import itemgetter, attrgetter
from surface3d_demo import plotSurface
from setting import *

#Pre-calculate distance matrix
D = np.zeros([MATRIX_SIZE, MATRIX_SIZE])
#PRE-CALCULATE SEMI Gen global matrix from date_from to date_to
G = np.zeros([MATRIX_SIZE, MATRIX_SIZE])
#PRE-CALCULATE COV Gen global matrix from date_from to date_to
G_COV = np.zeros([MATRIX_SIZE, MATRIX_SIZE])
#Contain temp of all Station
list_data = []
#list of mean data
list_mean = []
#Contain models for all area
global_data = {}
#Global curve trending ( z = ax + by + c )
trend_curve = [0,0,0]
sate_lite_deri = 0
sate_lite_value = 0
#Log file
f = open('log_universal.txt', 'w')
#FUNCTIONS
def generateGlobalMatrix( date_from, date_to, list_all_station):
	global trend_curve
	list_station = list_all_station
	#print list_station
	meteo_size = len(list_station)
	list_mean = []
	for i in xrange(0,meteo_size):
		#print list_station[i][0]
		item = getTempOfAAtationFromTo( list_station[i][3],date_from, date_to)
		list_all = zip(*item)
		#3 for temp, 4 for humid, 5 for rain
		list_temp = list_all[3]
		#print list_temp
		list_data.append(list_temp)
		mean_item = (list_all[1][0],list_all[2][0], sum(list_all[3])/len(list_all[3]))
		print mean_item
		list_mean.append(mean_item)
	f.write('MEAN: ' + str(list_mean) + '\n')
	trend_curve = curveFitting(list_mean)
	print trend_curve
	#plotSurface(trend_curve, list_mean)
	#print len(list_mean)
	#print list_data[0]
	#G = np.zeros([meteo_size, meteo_size])
	for x in xrange(0,meteo_size):#x 0->97 is Meteo_id 1->98
		for y in xrange(0,meteo_size):#0->97 is Meteo_id 1->98
			#gen covariance for [x][y]
			a = list_data[x]
			b = list_data[y]
			#cov =np.cov(a,b)[0][1]
			semi = semivariance( a, b)
			cov = covariance(a,b)
			#print 'a: ', a
			#print 'b: ',b
			#print 'cov a b = ', str(cov)
			#print covariance(a,b)
			G[x][y]= semi
			G_COV[x][y] = cov
	'''
	f.write('G_SEMI ----------------------------------------- \n')
	for item in G:
		f.write(str(item) + '\n')
	f.write('G_COV  ----------------------------------------- \n')
	for item in G_COV:
		f.write(str(item) + '\n')
	'''
	#print G[0:5,0:5]
	return trend_curve
def reGenerateSemiMatrix(list_all_station):
	G = np.zeros([MATRIX_SIZE, MATRIX_SIZE])
	a0, c0 = global_data[0][0], global_data[0][1]
	meteo_size = len(list_all_station)
	for x in xrange(0,meteo_size):#x 0->97 is Meteo_id 1->98
		for y in xrange(0,meteo_size):#0->97 is Meteo_id 1->98
			#semi = semivariance( a, b)
			#cov = covariance(a,b)
			h = D[x][y]#distance
			G_COV[x][y] = semiToCov( h, a0, c0)
			#print x, y, h, G_COV[x][y] 

#PRE-CALCULATE DISTANCE Gen all distance of all point
def generateDistanceMatrix(list_sta_by_area):
	#l = getAllObservation()
	l = list_sta_by_area
	meteo_size = len(l)
	D = np.zeros([meteo_size, meteo_size])
	for x in xrange(0,meteo_size):#0->97
		item1 = l[x]
		for y in xrange(0,meteo_size):#0->97
			item2 = l[y]
			d = haversine(item1[2], item1[1], item2[2], item2[1])
			D[x][y]= round(d)
			#print x, ' ', y, ' ', D[x][y]
			#time.sleep(0.5)
			#print d
	#print D[0:10,0:10]
	return D

def genModelForArea(area_id, list_station, list_data, G, D):
	print 'GEN MODEL FOR AREA ID ', area_id
	size_meteo = len(list_station)
	list_cov = []#covariance
	list_dis = []#distance
	list_dis.append(0)
	list_cov.append(0)
	for i in xrange(0,size_meteo):
		for j in xrange(i+1,size_meteo):
			#FILTER with distance > DISTANCE_BOUND km
			distance = D[i][j]
			if distance > DISTANCE_BOUND:
				continue
			idi = list_station[i][0]
			idj = list_station[j][0]
			list_cov.append(G[idi][idj])
			#print idi, idj, G[idi][idj]
			#time.sleep(1)
			list_dis.append(distance)
	#FIT ham bac 1
	z, mse_level_1 = genFitting(list_dis, list_cov, 1)	
	#FIT ham bac 2
	#z, mse_level_2 = genFitting(list_dis, list_cov, 2)
	#z = np.poly1d(np.polyfit(list_dis, list_cov, 2))

	xp = np.linspace(min(list_dis)//1, max(list_dis)//1, max(list_dis)//1)
	plt.subplot(3, 2, 3)
	plt.plot(xp, z(xp), 'r-')
	plt.xlabel('Distance(km)')
	plt.ylabel('semi-variogram (Ham bac 2)')
	#FIT ham bac 3
	z, mse_level_3 = genFitting(list_dis, list_cov, 3)
	#z = np.poly1d(np.polyfit(list_dis, list_cov, 3))
	xp = np.linspace(min(list_dis)//1, max(list_dis)//1, max(list_dis)//1)
	plt.subplot(3, 2, 4)
	plt.plot(xp, z(xp), 'r-')
	plt.xlabel('Distance(km)')
	plt.ylabel('semi-variogram (Ham bac 3)')
	plot_period(list_dis, list_cov, area_id)


#Krige one point
def krigeOne(point, neighbor, list_all_station, list_data, G, D):
	#print 'KRIGE ONE'
	list_station = list_all_station
	#Cal distances from current point to all others
	item0 = (0, point[0], point[1])
	meteo_size = len(list_station)
	list_d = []
	#cal all distance from point to others stations 
	for i in xrange(0,meteo_size):
		#Cal distance one-one
		item1 = list_station[i]
		d = haversine(item0[2], item0[1] ,item1[2], item1[1])
		newitem = (item1[0], d, item1[3], item1[1], item1[2])#id, distance, temp, lat, lon
		list_d.append(newitem)
	#Sort by distance, get n first nearest neighbors
	sorted_list = sorted(list_d, key=itemgetter(1))
	list_neighbor = sorted_list[:neighbor]
	#print list_neighbor
	K1 = np.zeros([neighbor, neighbor])
	K = np.zeros([neighbor, neighbor])
	k = np.zeros([neighbor, 1])
	k_semi = np.zeros([neighbor, 1])
	T = []# list of temp of neighbor station at interpolate time
	string = ''
	i = 0 
	for  item in list_neighbor:
		if LOG:
			f.write('getting T\n')
		#Nhiet do 1 thang cua tram item
		#print len(list_data)
		t = list_data[item[0]-1]
		trendValue = getTrendValue(trend_curve, item[3], item[4])
		#print trend_curve, trendValue
		if LOG:
			f.write(str(t) + '\n')
		t_size = len(t)
		T.append(t[t_size - 1] - trendValue)
		j = 0
		string = string + str(item[0])
		#print item
		#Area key = 0, because of we have only one model for all
		a0, c0 = global_data[0][0], global_data[0][1]
		h = item[1]#distance
		k[i][0] = semiToCov( h, a0, c0)
		k_semi[i][0] = spherical(h, a0, c0)
		for sub_item in list_neighbor:
			string = string+' ' + str(sub_item[0])
			#print i, j
			K1[i][j] = G_COV[item[0]-1][sub_item[0]-1]
			K [j][i] = K1[i][j]#Inverse of K1
			j = j + 1
		string = string + '\n'
		i = i + 1
	if LOG:
		f.write('T: ' + str(T) + '\n')
		f.write('neighbors list: \n' + string + '\n')
		#print string
		#print k
		#print K
	f.write('K: \n' + str(K) +' \n')
	f.write('k: \n' + str(k) +' \n')
	weight = np.dot(K,k)
	if LOG:
		f.write('ori-weight: \n' + str(weight) +' \n')
	if sum(weight) == 0:
		if LOG:
			f.write('NOT RELATED\n')
		weight[:] = 1 #assign the same weight for all elements
	weight = weight/sum(weight)
	krige = np.dot(T, weight)
	f.write('nor-weight: \n' + str(weight) +' \n')
	f.write('T: \n' + str(T)+' \n')
	f.write('krige: ' + str(krige)+' \n')
	#print krige
	#print krige[0],' ',
	#print k
	weight = inverseMatrix(weight)
	derivation = np.dot(weight, k_semi)
	f.write('derivation: ' + str(derivation[0][0])+' \n')	
	#time.sleep(2)
	return krige[0], derivation[0][0]
#DONE Find n neighbors base on (lat,lon)
#DONE Gen matrix Cij of neighbors inherit from G
#Gen Fit function with matrix Cij
#Gen matrix B (C[0,i]...)
#Gen Lamda matrix C*Lamda= B
#Calculate interpolated value

def plot_period(list_h,list_value, area_id):
	list_period_value= []
	list_period_h = []
	d = 10
	size_h = len(list_h)
	for x in xrange(0,int(max(list_h)//10)):
		mean = 0
		total = 0
		for y in xrange(0,size_h):
			if (list_h[y] > d*x) and (list_h[y] < d*(x+1)):
				total = total +1
				mean = mean + list_value[y]
		if total >0:
			list_period_value.append(mean/total)
			list_period_h.append(d*x)
	plt.subplot(3, 2, 1)
	plt.plot(list_h, list_value, 'r.')
	plt.title('A tale of x subplots')
	plt.ylabel('Semi-variogram')

	plt.subplot(3, 2, 2)
	plt.plot(list_period_h, list_period_value, 'r.')
	#plt.plot(list_h, list_value, 'r.')
	plt.xlabel('Distance (km)')
	plt.ylabel('Semi-variogram PERIOD')

	#spherical
  	a0,c0, mse_sph = opt('spherical', list_period_h, list_period_value)
  	#a0,c0, mse_sph = opt('spherical', list_h, list_value)
  	print 'a0=',a0, ' c0=', c0, ' mse_sph = ', mse_sph
	plt.subplot(3, 2, 5)
	list_spherical = []
	list_h = sorted(list_h)
	for h in list_h :
		list_spherical.append(spherical( h, a0, c0))
		#if spherical( h, a0, c0) != c0:
		#	print spherical( h, a0, c0)
	plt.plot(list_h, list_spherical, 'r-')
	plt.xlabel('Distance (km)')
	plt.ylabel('Semi-variogram- SPHERICAL')

	#plt.savefig(os.path.splitext(os.path.basename('temp_semi_all_station_thang_2'))[0] + '.png')
	sph = [a0, c0]
	global_data[area_id] = sph
	if LOG:
		plt.show()
def saveAsPng(Z):
	if LOG:
		plt.show()
	plt.clf()
	plt.savefig(os.path.splitext(os.path.basename('temp_sybthesize_view'))[0] + '.png')
	cdict = {'red':   ((0.0, 1.0, 1.0),
                   (0.5, 225/255., 225/255. ),
                   (0.75, 0.141, 0.141 ),
                   (1.0, 0.0, 0.0)),
         'green': ((0.0, 1.0, 1.0),
                   (0.5, 57/255., 57/255. ),
                   (0.75, 0.0, 0.0 ),
                   (1.0, 0.0, 0.0)),
         'blue':  ((0.0, 0.376, 0.376),
                   (0.5, 198/255., 198/255. ),
                   (0.75, 1.0, 1.0 ),
                   (1.0, 0.0, 0.0)) }
	#my_cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap',cdict,256)
	#fig, ax = plt.subplots()
	'''
	H = np.zeros_like( Z )
	minH = abs(Z).min()
	maxH = abs(Z).max()
	delta = maxH -minH
	for i in range( Z.shape[0] ):
	    for j in range( Z.shape[1] ):
	        H[i,j] = np.round( (255*(Z[i,j] - minH))/delta )
	Z = H
	'''
	Z = resampling(Z)
	#ax.matshow( Z, cmap=my_cmap, interpolation='nearest' )
	#ax.scatter( z.x/200.0, z.y/200.0, facecolor='none', linewidths=0.75, s=50 )
	#plt.xlim(0,99)
	#plt.ylim(0,80)
	#plt.xticks( [25,50,75], [5000,10000,15000] )
	#plt.yticks( [25,50,75], [5000,10000,15000] )
	# contour the gridded data, plotting dots at the nonuniform data points.
	#plt.subplot(3, 2, 6)
	xi = np.linspace(0,Z.shape[1],Z.shape[1])
	yi = np.linspace(0,Z.shape[0],Z.shape[0])
	CS = plt.contour(xi,yi,Z,10,linewidths=0.5,colors='k')
	CS = plt.contourf(xi,yi,Z,10,cmap=plt.cm.rainbow,vmax=abs(Z).max(), vmin=-abs(Z).max())
	plt.colorbar() # draw colorbar
	if LOG:
		plt.show()
	plt.savefig(os.path.splitext(os.path.basename('krige_thang_2'))[0] + '.png')
	#plt.savefig( 'krigingpurple.png', fmt='png', dpi=200 )
#MAIN PROGRAM
#PROCESSING
#1 GEN MODELS
def main_program(shuffi, isCrossValidation):
	f_se = open('f_se.txt', 'a')
	f_se.write('se statistic\n')
	f_da = open('f_da.txt', 'a')
	f_da.write('da statistic\n')

	list_all_test = shuffi[0]
	list_all_station = shuffi[1]
	global D
	print len(list_all_station)
	trend_curve = generateGlobalMatrix(date_from, date_to, list_all_station)
	D = generateDistanceMatrix(list_all_station)
	area_id = 0
	genModelForArea(area_id, list_all_station, list_data, G, D)
	reGenerateSemiMatrix(list_all_station)
	print 'GLOBAL DATA'
	print global_data
	derivation = np.zeros([row,col])
	result = np.zeros([row,col])
	result_kri_backup = np.zeros([row,col])
	for i in xrange(0,row):
		#print i
		for j in xrange(0, col):
			#print i, j
			point = (minLat + i*shift,minLon + j*shift)
			f.write(str(i)+' '+ str(j)+ ':'+ str(point)  +'\n')
			result[i][j], derivation[i][j] = krigeOne(point, neighbor, list_all_station, list_data, G, D)
			trendValue = getTrendValue(trend_curve, point[0], point[1])
			#print trendValue
			result[i][j] = result[i][j] + trendValue
			result_kri_backup[i][j] = result[i][j]
			#DATA ASSIMILATION: assimilate
			#if sate_lite_value[i][j] != 0:
			#	result[i][j] = assimilate(result[i][j], derivation[i][j], sate_lite_value[i][j], sate_lite_deri[i][j], f_da)
	#Assimilate with Utility.assimilate
	if isCrossValidation == False:
		exportGeotiff('test_t08_GEOTIFF_universal_kriging_assimilated', result, row, col, shift, minLon, minLat )
		exportGeotiff('test_t08_GEOTIFF_universal_kriging_derivation', derivation, row, col, shift, minLon, minLat )
	saveAsPng(result)
	saveAsPng(derivation)
	if isCrossValidation:	
		return calculateSE(result,result_kri_backup, list_all_test, minLat, minLon, shift, date_to, f, sate_lite_value, f_se)
	f_da.close()
	f_se.close()

def start(date_from_changed, date_to_changed, isCrossValidation):
	f = open('log_universal.txt', 'w')
	#INTERPOLATE
	global date_to
	global date_from
	global sate_lite_deri
	global sate_lite_value
	date_from = date_from_changed
	date_to = date_to_changed
	print date_from, date_to
	list_all_station = getAllObservation()
	sate_lite_deri, z_sate_to_surface = getSateliteDeriMap()
	print z_sate_to_surface
	global sate_lite_value
	sate_lite_value = get_sate_lite_value(date_to, z_sate_to_surface)

	#shulf for ten-fold cross validation
	if isCrossValidation:
		shuff_dic = slide(FOLD, list_all_station)
		se = 0
		se_satelite = 0
		se_sate_count = 0
		for x in xrange(0,len(shuff_dic)):
			print str(FOLD) + '-FOLD: '+ str(x) +' -------------------------'
			#for item in shuff_dic[x]:
			#	print item, '\n'
			se_normal, se_sate_i, se_sate_count_i = main_program(shuff_dic[x], isCrossValidation)
			se = se + se_normal
			if se_sate_i != 0:
				se_satelite = se_satelite + se_sate_i
				se_sate_count = se_sate_count + se_sate_count_i
			if se_sate_count != 0:
				print 'LOOP SE: ', str(se/(x+1)), 'SE_SATE: ', str(se_satelite/se_sate_count)
		print 'SE: ', str(se/FOLD), 'SE_SATE: ', str(se_satelite/se_sate_count)
		f.write('SE: ' + str(se/FOLD) + '\n')
		f.write('SE_SATE: '+ str(se_satelite/se_sate_count))
	else:
		item = [[], reIndex(list_all_station)]
		#item = [[], list_all_station]
		main_program(item, isCrossValidation)
	f.close()
#************************************************************************************************
start(date_from, date_to, isCrossValidation)
#************************************************************************************************
