#Simple Kringing Implementation
import numpy as np
import time, os
import matplotlib.pyplot as plt
from get_data import getTempOfAAtationFromTo,isInVietnam,getAreaIdFromPoint
from get_data import getAllObservation,getAllStaByAreaId
from Utility import haversine, covariance, semivariance, opt,spherical, genFitting, semiToCov
from operator import itemgetter, attrgetter

#SETTING
MATRIX_SIZE = 100
LAT_MIN = 8.4
LAT_MAX = 23.4
LON_MIN = 102.1
LON_MAX = 109.4
date_from= '2011-02-01' # for all pairs
date_to = '2011-02-28'  # for all pairs
#date_from= '2011-01-01'
#date_to = '2011-01-15'
neighbor = 10
#Contain temp of all Station
list_data = []
#Contain all (Global matrix, Distance matrix, Model) for each Area 
global_data = {}
#PRE-CALCULATE COV Gen global matrix from date_from to date_to
def generateGlobalMatrix( date_from, date_to, list_sta_by_area):
	#list_station = getAllObservation()
	list_station = list_sta_by_area
	#print list_station
	meteo_size = len(list_station)
	for i in xrange(0,meteo_size):
		print list_station[i][0]
		item = getTempOfAAtationFromTo( list_station[i][0],date_from, date_to)
		list_all = zip(*item)
		#3 for temp, 4 for humid, 5 for rain
		list_temp = list_all[3]
		#print list_temp
		#time.sleep(10)
		list_data.append(list_temp)
	#print list_data[0]
	G = np.zeros([meteo_size, meteo_size])
	for x in xrange(0,meteo_size):#x 0->97 is Meteo_id 1->98
		for y in xrange(0,meteo_size):#0->97 is Meteo_id 1->98
			#gen covariance for [x][y]
			a = list_data[x]
			b = list_data[y]
			#cov =np.cov(a,b)[0][1]
			semi = semivariance( a, b)
			#print 'a: ', a
			#print 'b: ',b
			#print 'cov a b = ', str(cov)
			#print covariance(a,b)
			G[x][y]= semi
	print G[0:5,0:5]
	return G
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
	print D[0:10,0:10]
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
			#FILTER with distance > 600km
			distance = D[i][j]
			#if distance > 600:
			#	continue
			list_cov.append(G[i][j])
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
	print 'KRIGE ONE'
	list_station = list_all_station
	#Cal distances from current point to all others
	item0 = (0, point[0], point[1])
	meteo_size = len(list_station)
	list_d = []
	for i in xrange(0,meteo_size):
		#Cal distance one-one
		item1 = list_station[i]
		d = haversine(item0[2], item0[1] ,item1[2], item1[1])
		newitem = (item1[0], d, getAreaIdFromPoint([item1[1], item1[2]]))
		list_d.append(newitem)
	#Sort by distance, get n first nearest neighbors
	sorted_list = sorted(list_d, key=itemgetter(1))
	list_neighbor = sorted_list[:neighbor]
	for  item in list_neighbor:
		print item
		#get a0, c0 from compatitie model
		a0, c0 = global_data[item[2][0]][0], global_data[item[2][0]][1]
		#print global_data[item[2][0]]
		value = spherical( item[1], a0, c0)
		print value

	'''
	list_all = zip(*list_neighbor)
	list_id = list_all[0]	
	#print list_id
	#Gen matrix Cij of neighbors inherit from G
	C = np.zeros([neighbor, neighbor])
	for x in xrange(0, neighbor):
		i = list_id[x]
		for y in xrange(0, neighbor):
			#Cal Cij
			j = list_id[y]
			C[x][y] = G[i-1][j-1]
	#print C
	#Gen Fit function
	list_cov = []#covariance
	list_dis = []#distance
	for i in xrange(0,neighbor):
		for j in xrange(i+1,neighbor):
			#FILTER with distance > 600km
			distance = D[list_id[i]-1][list_id[j]-1]
			if distance > 600:
				continue
			list_cov.append(C[i][j])
			list_dis.append(D[list_id[i]-1][list_id[j]-1])
	#FIT ham bac 1
	z, mse_level_1 = genFitting(list_dis, list_cov, 1)	
	#FIT ham bac 2
	z, mse_level_2 = genFitting(list_dis, list_cov, 2)
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
	plot_period(list_dis, list_cov)
	'''
#DONE Find n neighbors base on (lat,lon)
#DONE Gen matrix Cij of neighbors inherit from G
#Gen Fit function with matrix Cij
#Gen matrix B (C[0,i]...)
#Gen Lamda matrix C*Lamda= B
#Calculate interpolated value

def plot_period(list_h,list_value, area_id):
	'''
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
	'''
	plt.subplot(3, 2, 1)
	plt.plot(list_h, list_value, 'r.')
	plt.title('A tale of x subplots')
	plt.ylabel('Semi-variogram')

	plt.subplot(3, 2, 2)
	#plt.plot(list_period_h, list_period_value, 'r.')
	plt.plot(list_h, list_value, 'r.')
	plt.xlabel('Distance (km)')
	plt.ylabel('Semi-variogram PERIOD')

	#spherical
  	#a0,c0, mse_sph = opt('spherical', list_period_h, list_period_value)
  	a0,c0, mse_sph = opt('spherical', list_h, list_value)
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
	#plt.show()




#MAIN PROGRAM
#Test with Ha Noi (lat, lon)
hanoi = (21.0226967,105.8369637)
#Test with random 
other = (20.8428174,105.3252411)
danang = (16.0466742,108.2064774)
hcm = (10.7502375,106.5638999)
playcu = (13.9621941,107.9699348)
points = []
points.append(hanoi)
points.append(other)
points.append(hcm)
points.append(playcu)
points.append(danang)

#PROCESSING
for x in xrange(1,9):
	area_id = x
	list_station = getAllStaByAreaId(area_id)
	if x == 2:
		print 'break'
		continue
	G = generateGlobalMatrix(date_from, date_to, list_station)
	D = generateDistanceMatrix(list_station)
	genModelForArea(area_id, list_station, list_data, G, D)
print 'GLOBAL DATA'
print global_data
list_all_station = getAllObservation()
print len(list_all_station)
krigeOne(hcm, neighbor, list_all_station, list_data, G, D)

#area_id = 1

#list_station = getAllStaByAreaId(area_id)
#G = generateGlobalMatrix(date_from, date_to, list_station)
#D = generateDistanceMatrix(list_station)

#for item in points:
#	krigeOne(item,neighbor,list_station, list_data, G, D)
#krigeOne(hcm,neighbor,list_station, list_data, G, D)
#genModelForArea(area_id, list_station, list_data, G, D)
