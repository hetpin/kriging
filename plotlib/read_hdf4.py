#Read hdf4 with LOG
# -*- coding: utf-8 -*-
#!/usr/local/bin/python

#LINKS
#http://www.ajdesigner.com/phphumidity/dewpoint_equation_relative_humidity.php#ajscroll
#http://hdfeos.org/zoo/index_openLAADS_Examples.php
#http://jgomezdans.github.io/gdal_notes/ipython.html
#
from osgeo import gdal 
import matplotlib.pyplot as plt 
import datetime
from operator import itemgetter, attrgetter
from get_data import getAllObservation
import os, time
import psycopg2, sys
import numpy as np
from Utility import convertTimeEpochToNormal
SDS_NAME  = "Retrieved_Moisture_Profile"
FILL_VALUE_KEY = '_FillValue'
ADD_OFFSET_KEY = 'add_offset'
SCALE_FACTO_KEY = 'scale_factor'
#Dew-point temperature to Relative humidity 
#Input: T-Temperature; Tdp-Dew-point Temperature
#Out: RH(%)
P_level_max = 20
P_Level = [5., 10., 20., 30., 50., 70., 100., 150., 200., 250., 300., 400., 500., 620., 700., 780., 850., 920., 950., 1000.]

def dpToRH(T, Tdp):
	return 100*(((112-0.1*T+Tdp)/(112+0.9*T))**8)
#Find the closest p_level of hpa
def hpaToLevel(hpa, P_Level):
	list_ = []
	i = 1
	for item in P_Level:
		list_.append([i, abs(item-hpa)])
		i = i + 1
	sorted_list = sorted(list_, key=itemgetter(1))
	return sorted_list[0][0]
def read_a_file(list_obs,file_name):
	f = open('log_read_mod07l2.txt', 'w')
	list_ = []
	#gdal_dataset = gdal.Open ("/data/geospatial_10/ucfajlg/MOD12/MCD12Q1.A2005001.h17v03.005.2008310174635.hdf")
	gdal_dataset = gdal.Open (file_name)
	#print gdal_dataset.GetSubDatasets()
	lc_data = gdal.Open ( 'HDF4_EOS:EOS_SWATH:"' + file_name+'":mod07:Retrieved_Moisture_Profile')
	lc_data_temp = gdal.Open ( 'HDF4_EOS:EOS_SWATH:"' + file_name+'":mod07:Surface_Temperature')
	lc_data_pressure = gdal.Open ( 'HDF4_EOS:EOS_SWATH:"' + file_name+'":mod07:Surface_Pressure')
	lc_data_time = gdal.Open ( 'HDF4_EOS:EOS_SWATH:"' + file_name+'":mod07:Scan_Start_Time')
	lc_data_lat = gdal.Open ( 'HDF4_EOS:EOS_SWATH:"' + file_name+'":mod07:Latitude')
	lc_data_lon = gdal.Open ( 'HDF4_EOS:EOS_SWATH:"' + file_name+'":mod07:Longitude')

	band_0 = lc_data.GetRasterBand(20)
	band_0_arr = band_0.ReadAsArray()
	temp_arr = lc_data_temp.ReadAsArray()
	
	pressure_arr = lc_data_pressure.ReadAsArray()
	time_arr = lc_data_time.ReadAsArray()
	lat_arr = lc_data_lat.ReadAsArray()
	lon_arr = lc_data_lon.ReadAsArray()
	#print time_arr[0][0]
	start_date_time = convertTimeEpochToNormal(int(time_arr[0][0]))
	#print start_date_time
	row = band_0_arr.shape[0]
	col = band_0_arr.shape[1]
	list_lat = [lat_arr[0][0],lat_arr[0][col-1], lat_arr[row-1][0], lat_arr[row-1][col-1]]
	list_lon = [lon_arr[0][0],lon_arr[0][col-1], lon_arr[row-1][0], lon_arr[row-1][col-1]]
	min_lat = min(list_lat)
	min_lon = min(list_lon)
	max_lat = max(list_lat)
	max_lon = max(list_lon)
	shirf_lat = (max_lat- min_lat)/row
	shitf_lon = (max_lon- min_lon)/col
	window = 20
	#f.write("\nlc_data_band0\n")
	#print lc_data.RasterCount
	#f.write(str(lc_data.GetMetadata()))
	#f.write('\nlc_data_temp\n')

	temp_fill_value = float(lc_data_temp.GetMetadata().get(FILL_VALUE_KEY))
	temp_add_offset = float(lc_data_temp.GetMetadata().get(ADD_OFFSET_KEY))
	temp_scale_factor = float(lc_data_temp.GetMetadata().get(SCALE_FACTO_KEY))

	moisture_fill_value = float(lc_data.GetMetadata().get(FILL_VALUE_KEY))
	moisture_add_offset = float(lc_data.GetMetadata().get(ADD_OFFSET_KEY))
	moisture_scale_factor = float(lc_data.GetMetadata().get(SCALE_FACTO_KEY))

	pressure_fill_value = float(lc_data_pressure.GetMetadata().get(FILL_VALUE_KEY))
	pressure_add_offset = float(lc_data_pressure.GetMetadata().get(ADD_OFFSET_KEY))
	pressure_scale_factor = float(lc_data_pressure.GetMetadata().get(SCALE_FACTO_KEY))

	list_point = []
	for i in xrange(0,row):
		for j in xrange(0,col):
			if pressure_arr[i][j] != pressure_fill_value:
				#Get pressure
				pressure_arr[i][j] = pressure_scale_factor*(pressure_arr[i][j]-pressure_add_offset)
				#Convert hpa to level
			else:
				pressure_arr[i][j] = 0
			if(temp_arr[i][j] != temp_fill_value) and (band_0_arr[i][j] != moisture_fill_value):
				temp = temp_scale_factor*(temp_arr[i][j]-temp_add_offset) - 273.15
				moisture = moisture_scale_factor*(band_0_arr[i][j]-moisture_add_offset) - 273.15
				moisture = dpToRH(temp, moisture)
				item = [i, j, temp, moisture]
				list_point.append(item)
	#Find value for a station
	for item in list_obs:
		#print 'Item',item 
		lat = item[1]
		lon = item[2]
		if lat < min_lat or lat > max_lat or lon < min_lon or lon > max_lon:
			#print 'OUT OF RANGE', min_lat, max_lat, min_lon, max_lon
			continue
		result = (item[0], -1,-1,-1,-1, -1, -1, 1000)#Store result: id, lat, lon, temp, moisture, i, j, distance
		list_result = []
		radius = 0.05# 
		for item in list_point:
			i = item[0]
			j = item[1]
			temp = item[2]
			moisture = item[3]
			if abs(lat-lat_arr[i][j]) > radius or abs(lat-lat_arr[i][j]) > radius:
				continue
			distance = (abs(lat-lat_arr[i][j])**2 + abs(lon-lon_arr[i][j])**2)**0.5
			#print i, j, distance, lat_arr[i][j], lon_arr[i][j]
			#Find the min value
			if distance<radius:
				list_result.append((item[0], lat_arr[i][j], lon_arr[i][j], temp, moisture, i, j, distance))
		if len(list_result)!= 0:
			#print len(list_result)
			sum_temp = 0
			sum_moisture = 0
			for item in list_result:
				sum_temp = sum_temp + item[3]
				sum_moisture = sum_moisture + item[4]
			#print sum_temp/len(list_result), sum_moisture/len(list_result)
			list_.append((start_date_time.date(), start_date_time.time(),result[0], sum_temp/len(list_result), sum_moisture/len(list_result), 0))
	f.close()
	plt.imshow (band_0_arr, interpolation='nearest', vmin=0, cmap=plt.cm.gist_earth)
	plt.colorbar()
	plt.show()
	plt.imshow (temp_arr, interpolation='nearest', vmin=0, cmap=plt.cm.gist_earth)
	plt.colorbar()
	plt.show()
	#plt.imshow (pressure_arr, interpolation='nearest', vmin=0, cmap=plt.cm.gist_earth)
	#plt.colorbar()
	#plt.show()
	for item in list_:
		print item
	#insertTerraToDB(list_)
def insertTerraToDB(list_):
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres')
	    cur = con.cursor()  
	    query = "INSERT INTO terra_2 ( terra_date, terra_time,terra_station_id, terra_temp, terra_humid, terra_rain) VALUES ( %s, %s, %s,%s,%s,%s)"
	    cur.executemany(query, list_)
	    con.commit()
	except psycopg2.DatabaseError, e:
	    if con:
	        con.rollback()
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    if con:
	        con.close()
	print 'GOT ', len(list_)
#Main
#List of observation (id, lat, lon, area_id, alt)
list_obs = getAllObservation()
dir_path="D:\Thanhnx\Disk_uet\ThanhUET\Dropbox 2012\Dropbox\Master\Research\DuBaoChayRung\DuLieuVeTinh\MOD07L2\\2011_Terra_01"  # insert the path to the directory of interest here
dirList=os.listdir(dir_path)
time.sleep(10)
for fname in dirList:
	print fname
	read_a_file(list_obs, dir_path + "\\"+ fname)