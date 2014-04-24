# -*- coding: utf-8 -*-
import os
import datetime
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
#IMPORTING variable
list_ = []
index = 0
f = open('workfile.txt', 'w')


for line in fileinput.input(glob.glob("data_terra/*.xls")):
	search = '.xls' #Tim tung thang cho nay//BT010111
	if fileinput.filename().find(search) != -1:
		print '-Start for-'
	else:
		continue
	if fileinput.isfirstline(): # first in a file?
		sys.stderr.write("-- reading %s --\n" % fileinput.filename())
	workbook = xlrd.open_workbook(fileinput.filename())
	worksheet = workbook.sheet_by_name('Surface_Temperature')
	worksheet_humid = workbook.sheet_by_name('Surface_Temperature')#('Water_Vapor')//treat- Vi cho nay quen k gen Vapor info :D
	num_rows = worksheet.nrows - 1
	print 'num_rows = ', num_rows
	num_cells = worksheet.ncols - 1
        #testing purpose
        curr_row = -1 #start at -1
        num_rows = num_rows #end   at num_rows
        while curr_row < num_rows:
			curr_row += 1
			row = worksheet.row(curr_row)
			row_water = worksheet_humid.row(curr_row)
			print 'Row:', curr_row, ' num_cells ', num_cells
			curr_cell = -1
			terra_date = ''
			terra_time = ''
			while curr_cell < num_cells:
				curr_cell += 1
				# Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
				cell_type = worksheet.cell_type(curr_row, curr_cell)
				cell_value = worksheet.cell_value(curr_row, curr_cell)
				cell_value_water = worksheet_humid.cell_value(curr_row, curr_cell)
				terra_station_id = curr_cell -1
				terra_temp_13 = cell_value
				terra_id = index
				terra_humid = 0
				terra_rain = 0
#				print '	', curr_cell, ':', cell_type, ':', cell_value
				if curr_cell == 0 :
#					print cell_value
					a1_as_datetime = datetime.datetime(*xlrd.xldate_as_tuple(cell_value, workbook.datemode))
					#print a1_as_datetime.date()
					#print a1_as_datetime.time()
					terra_date = a1_as_datetime.date()
					continue
				if curr_cell == 1 :
					cell_value = cell_value + 40544
#					print cell_value
					a2_as_datetime = datetime.datetime(*xlrd.xldate_as_tuple(cell_value, workbook.datemode))
					#print a2_as_datetime.time()
					#terra_time = '00-00-0000 ' + str(a2_as_datetime.time())
					terra_time = a2_as_datetime.time()
					#print terra_time
					continue
				else:
					if cell_type != 0:
						print '	', curr_cell, ':', cell_type, ':', cell_value, ' station_id = ', curr_cell -1, ' humid :',cell_value_water 
						list_.append((terra_id, terra_date, terra_time,terra_station_id, terra_temp_13 -273.15, cell_value_water, terra_rain))
						index = index + 1
#	for item in list_:
#		pprint (vars(item))
con = None
try:
    con = psycopg2.connect(database='fimo_db', user='postgres') 
  
    cur = con.cursor()  
    
    query = "INSERT INTO terra (terra_id, terra_date, terra_time,terra_station_id, terra_temp, terra_humid, terra_rain) VALUES (%s, %s, %s, %s,%s,%s,%s)"
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