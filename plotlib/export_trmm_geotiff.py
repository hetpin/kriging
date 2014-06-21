#Export trmm geotiff
import numpy as np
from Utility import exportGeotiff, resampling
def read_integers(filename):
	return map(int, open(filename).read().split())
#SETTING
minLat = 5 #oy
maxLat = 25
minLon = 100 # ox
maxLon = 110
shift = 0.25 # grid
row = int((maxLat-minLat)/shift)
col = int((maxLon-minLon)/shift)
#list =  read_integers('output_trmm_test.txt')
list =  read_integers('output_trmm.txt')
list_geo_1 = list[:len(list)/2]
list_geo_2 = list[len(list)/2:]
print len(list)
print len(list_geo_1)
print len(list_geo_2)
print row, col
geo_1 = np.zeros([row,col])
geo_2 = np.zeros([row,col])
geo_1_T = np.zeros([row,col])
geo_2_T = np.zeros([row,col])
for i in xrange(0,col):
	#print i
	for j in xrange(0, row):
		#print i-col, j-row
		geo_1[j][i] = list_geo_1[i*row+j]
		geo_2[j][i] = list_geo_2[i*row+j]
for i in xrange(0,row):
	#print i
	for j in xrange(0, col):
		#print i, j, row - j - 1
		geo_1_T[i][j] = geo_1[row-i-1][j]
		geo_2_T[i][j] = geo_2[row-i-1][j]
		print geo_1_T[i][j]
#exportGeotiff('geo_1_9years', resampling(geo_1_T), row, col, shift, minLon, minLat)
#exportGeotiff('geo_2_9years_Mar', resampling(geo_2_T), row, col, shift, minLon, minLat)
exportGeotiff('geo_1_9years_avg', geo_1_T/9, row, col, shift, minLon, minLat)
exportGeotiff('geo_2_9years_Mar_avg', geo_2_T/9, row, col, shift, minLon, minLat)
