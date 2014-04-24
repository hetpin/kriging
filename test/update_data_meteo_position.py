# -*- coding: utf-8 -*-
import fileinput
import glob
import string, sys
import xlrd
import psycopg2
from Row import Row
from pprint import pprint
curr_row = -1
list_root = []
empty_string = '-'


search = 'BT010111_position.xls'
workbook = xlrd.open_workbook(search)
worksheet = workbook.sheet_by_name('Sheet1')
num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
list_data = []
#testing purpose
curr_row = 1 #start at 1
num_rows = 99 #end   at 99
while curr_row < num_rows:
	curr_row += 1
	row = worksheet.row(curr_row)
#	print 'Row:', curr_row
	curr_cell = -1
	row_data  = Row(curr_row, "name_tinh", "name_tram", 13, 23, 33, 43,"file_name", 0, 0, 0 , 0 , 0)
	while curr_cell < num_cells:
		curr_cell += 1
		# Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
		cell_type = worksheet.cell_type(curr_row, curr_cell)
		cell_value = worksheet.cell_value(curr_row, curr_cell)
#				print '	', curr_cell, ':', cell_type, ':', cell_value
		if curr_cell == 0 :
			row_data.id = cell_value
		if curr_cell == 1 :
			if cell_type == 0:
				row_data.name_tinh = list_data[-1].name_tinh
			else:
				row_data.name_tinh = cell_value
		if curr_cell == 2 :
			row_data.name_tram = cell_value
		if curr_cell == 3 :
			if cell_value == empty_string:
				row_data.temp_13 = 0
			else:
				row_data.temp_13 = cell_value
			if cell_type == 0:
				row_data.temp_13 = 0
		if curr_cell == 4 :
			if cell_value == empty_string:
				row_data.humid_13 = 0
			else:
				row_data.humid_13 = cell_value
			if cell_type == 0:
				row_data.humid_13 = 0
		if curr_cell == 5 :
			if cell_value == empty_string:
				row_data.rain_13 = 0
			else:
				row_data.rain_13 = cell_value
			if cell_type == 0:
				row_data.rain_13 = 0						
		if curr_cell == 6 :
			if cell_value == empty_string:
				row_data.rain_24 = 0
			else:
				row_data.rain_24 = cell_value
			if cell_type == 0:
				row_data.rain24 = 0
		if curr_cell == 7 :
			row_data.file_name = cell_value
		if curr_cell == 8 :
			if cell_type == 0:
				row_data.lat = 0
			else :
				row_data.lat = cell_value
		if curr_cell == 9 :
			if cell_type == 0:
				row_data.lon = 0
			else :
				row_data.lon = cell_value
		if curr_cell == 10 :
			if cell_type == 0:
				row_data.alt = 0
			else :
				row_data.alt = cell_value
		if curr_cell == 11:
			if cell_type == 0:
				row_data.utmx = 0
			else :
				row_data.utmx = cell_value
		if curr_cell == 12:
			if cell_type == 0:
				row_data.utmy = 0
			else :
				row_data.utmy = cell_value
	if row_data.alt != 0:
		list_data.append(row_data)
#for item in list_data:
#	pprint (vars(item))
f = open('workfile.txt', 'w')
index = 0
for small_item in list_data:
	index = index + 1
	f.write(str(small_item.id) + ' ' + small_item.file_name+' '+ small_item.name_tinh+ ' '+ small_item.name_tram + ' '+ str(small_item.utmx)+ '\n' )

#IMPORTING
list_ = []
for item in list_data:
	list_.append((item.id, item.name_tram, item.name_tinh, item.lat, item.lon, item.alt, item.file_name,item.utmx, item.utmy))
con = None
try:
	con = psycopg2.connect(database='fimo_db', user='postgres') # for default localhost
	#con = psycopg2.connect(database='fimo_fire', user='uet', password = 'uet123', host = '192.168.3.190', port = 5432)
	updated = 0
	cur = con.cursor()
	for item in list_data:
		print 'updating ', item.id, item.name_tram, str(item.utmx) 
		cur.execute("UPDATE station SET station_lat=%s ,station_long = %s,station_alt =%s, station_utmx =%s, station_utmy=%s WHERE station_id=%s", (item.lat,item.lon, item.alt,item.utmx, item.utmy, item.id))
		con.commit()
		updated =updated + cur.rowcount
	print updated
except psycopg2.DatabaseError, e:    
	if con:
		con.rollback()    
		print 'Error %s' % e    
		sys.exit(1)
    
    
finally:
	
	if con:
		con.close()