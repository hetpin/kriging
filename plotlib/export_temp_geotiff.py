#export_temp_geotiff
import numpy as np
from get_data import getAvgAllStationAMonth
from Utility import exportGeotiff, resampling, interpolate
#SETTING
minLat = 5 #oy
maxLat = 25
minLon = 100 # ox
maxLon = 110
shift = 0.1 # grid
row = int((maxLat-minLat)/shift)
col = int((maxLon-minLon)/shift)

list = getAvgAllStationAMonth(3)
list_all = zip(*list)
list_temp = list_all[3]
avg= sum(list_temp)/len(list_temp)
#for item in list:
#	print item
grid = interpolate(list, row, col, shift, minLon, minLat, avg)
exportGeotiff('geo_temp_avg_all_one_month_Mar', grid, row, col, shift, minLon, minLat)
#exportGeotiff('geo_2_9years_Mar', resampling(geo_2_T), row, col, shift, minLon, minLat)
