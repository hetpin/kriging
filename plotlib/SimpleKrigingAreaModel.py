#Simple Kringing Implementation
import numpy as np
import time, os
import matplotlib
import matplotlib.pyplot as plt
from get_data import getTempOfAAtationFromTo,isInVietnam,getAreaIdFromPoint
from get_data import getAllObservation,getAllStaByAreaId
from Utility import haversine, covariance, semivariance, opt,spherical, genFitting, semiToCov, curveFitting,inverseMatrix,exportGeotiff,resampling
from operator import itemgetter, attrgetter
from surface3d_demo import plotSurface

#SETTING
MATRIX_SIZE = 100
LAT_MIN = 8.4
LAT_MAX = 23.4
LON_MIN = 102.1
LON_MAX = 109.4
date_from= '2011-11-01' # for all pairs
date_to = '2011-11-28'  # for all pairs
#date_from= '2011-01-01'
#date_to = '2011-01-15'
neighbor = 10
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
trend_curve = 0
#Log file
f = open('log_area_model.txt', 'w')

#FUNCTIONS
def generateGlobalMatrix( date_from, date_to, list_all_station):
	list_station = list_all_station
	#print list_station
	meteo_size = len(list_station)
	list_mean = []
	for i in xrange(0,meteo_size):
		#print list_station[i][0]
		item = getTempOfAAtationFromTo( list_station[i][0],date_from, date_to)
		list_all = zip(*item)
		#3 for temp, 4 for humid, 5 for rain
		list_temp = list_all[3]
		#print list_temp
		list_data.append(list_temp)
		mean_item = (list_all[1][0],list_all[2][0], sum(list_all[3])/len(list_all[3]))
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
	#return G
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
		newitem = (item1[0], d, item1[3])
		list_d.append(newitem)
	#Sort by distance, get n first nearest neighbors
	sorted_list = sorted(list_d, key=itemgetter(1))
	list_neighbor = sorted_list[:neighbor]
	#print list_neighbor
	'''
	#Get areaid for each station
	list_neighbor_with_areaid = []
	for item in list_neighbor:
		item1 = list_station[item[0]]
		new_item = (item[0], item[1], getAreaIdFromPoint([item1[1], item1[2]]))
		list_neighbor_with_areaid.append(new_item)
	'''
	K1 = np.zeros([neighbor, neighbor])
	K = np.zeros([neighbor, neighbor])
	k = np.zeros([neighbor, 1])
	T = []# list of temp of neighbor station at interpolate time
	string = ''
	i = 0 
	for  item in list_neighbor:
		f.write('getting T\n')
		#Nhiet do 1 thang cua tram item
		#print len(list_data)
		t = list_data[item[0]-1]
		f.write(str(t) + '\n')
		t_size = len(t)
		T.append(t[t_size - 1])
		j = 0
		string = string + str(item[0])
		#print item
		a0, c0 = global_data[item[2]][0], global_data[item[2]][1]
		h = item[1]#distance
		k[i][0] = semiToCov( h, a0, c0)
		for sub_item in list_neighbor:
			string = string+' ' + str(sub_item[0])
			#print i, j
			K1[i][j] = G_COV[item[0]-1][sub_item[0]-1]
			K [j][i] = K1[i][j]#Inverse of K1
			j = j + 1
		string = string + '\n'
		i = i + 1
	f.write('neighbors list: \n' + string + '\n')
	#print string
	#print k
	#print K
	f.write('K: \n' + str(K) +' \n')
	f.write('k: \n' + str(k) +' \n')
	weight = np.dot(K,k)
	f.write('ori-weight: \n' + str(weight) +' \n')
	if sum(weight) == 0:
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
	derivation = np.dot(weight, k)
	f.write('derivation: ' + str(derivation[0][0])+' \n')	
	#time.sleep(2)
	return krige[0], derivation[0][0]


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
def saveAsPng(Z):
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
	plt.show()
	plt.savefig(os.path.splitext(os.path.basename('krige_thang_2'))[0] + '.png')
	#plt.savefig( 'krigingpurple.png', fmt='png', dpi=200 )




#MAIN PROGRAM
#Test with Ha Noi (lat, lon)
hanoi = (21.0226967,105.8369637)
#Test with random 
other = (20.8428174,105.3252411)
danang = (16.0466742,108.2064774)
hcm = (10.7502375,106.5638999)
playcu = (13.9621941,107.9699348)
points = []
points.append(hcm)
points.append(hanoi)
points.append(other)
points.append(playcu)
points.append(danang)

#PROCESSING
#1 GEN MODELS
list_all_station = getAllObservation()
print len(list_all_station)
generateGlobalMatrix(date_from, date_to, list_all_station)
for x in xrange(1,9):
	area_id = x
	list_station = getAllStaByAreaId(area_id)
	if x == 2:
		print 'break'
		continue
	#G = generateGlobalMatrix(date_from, date_to, list_station)
	D = generateDistanceMatrix(list_station)
	genModelForArea(area_id, list_station, list_data, G, D)
print 'GLOBAL DATA'
print global_data
#INTERPOLATE
minLat = 8.4
maxLat = 23.6
minLon = 102.1
maxLon = 109.8
shift = 0.1
row = int((maxLat-minLat)/shift)
col = int((maxLon-minLon)/shift)
xi = np.linspace(minLon,maxLon,shift)
yi = np.linspace(minLat,maxLat,shift)
derivation = np.zeros([row,col])
result = np.zeros([row,col])
for i in xrange(0,row):
	print i
	for j in xrange(0, col):
		#print i, j
		point = (minLat + i*shift,minLon + j*shift)
		f.write(str(i)+' '+ str(j)+ ':'+ str(point)  +'\n')
		#if isInVietnam(point):
		result[i][j], derivation[i][j] = krigeOne(point, neighbor, list_all_station, list_data, G, D)
f.close()
#exportGeotiff('filename', raster, row, col, shift, minLon, minLat)
exportGeotiff('t8_GEOTIFF_krige_AREA_MODEL', result, row, col, shift, minLon, minLat )
saveAsPng(result)
saveAsPng(derivation)


#for point in points:
#	value = 0
#	if isInVietnam(point):
#		value = krigeOne(point, neighbor, list_all_station, list_data, G, D)
	
	#time.sleep(5)

#area_id = 1

#list_station = getAllStaByAreaId(area_id)
#G = generateGlobalMatrix(date_from, date_to, list_station)
#D = generateDistanceMatrix(list_station)

#for item in points:
#	krigeOne(item,neighbor,list_station, list_data, G, D)
#krigeOne(hcm,neighbor,list_station, list_data, G, D)
#genModelForArea(area_id, list_station, list_data, G, D)
