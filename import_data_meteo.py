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


for line in fileinput.input(glob.glob("data/*.xls")):
	search = 'BT010111.xls' #Tim tung thang cho nay
	if fileinput.filename().find(search) != -1:
		print '-Start for-'
	else:
		continue
	if fileinput.isfirstline(): # first in a file?
		sys.stderr.write("-- reading %s --\n" % fileinput.filename())
	workbook = xlrd.open_workbook(fileinput.filename())
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
			print 'Row:', curr_row
			curr_cell = -1
			row_data  = Row(curr_row, "name_tinh", "name_tram", 13, 23, 33, 43,"file_name", 0, 0, 0)
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
				if curr_cell == 4 :
					if cell_value == empty_string:
						row_data.humid_13 = 0
					else:
						row_data.humid_13 = cell_value
				if curr_cell == 5 :
					if cell_value == empty_string:
						row_data.rain_13 = 0
					else:
						row_data.rain_13 = cell_value
				if curr_cell == 6 :
					if cell_value == empty_string:
						row_data.rain_24 = 0
					else:
						row_data.rain_24 = cell_value
				if curr_cell == 7 :
					row_data.file_name = cell_value
			list_data.append(row_data)
#	for item in list_data:
#		pprint (vars(item))
	list_root.append(list_data)
f = open('workfile.txt', 'w')
for item in list_root:
	index = 0
	for small_item in item:
		index = index + 1
		f.write( small_item.file_name+' '+ small_item.name_tinh+ ' '+ small_item.name_tram + '\n' )

#IMPORTING
list_import = list_root[0]
list_ = []
for item in list_import:
	list_.append((item.id, item.name_tram, item.name_tinh, '0', '0', item.file_name))
con = None
try:
     
    con = psycopg2.connect(database='fimo_db', user='postgres') 
  
    cur = con.cursor()  
    
#    cur.execute("DROP TABLE IF EXISTS cars")
#    cur.execute("CREATE TABLE cars(id INT PRIMARY KEY, name TEXT, price INT)")
    query = "INSERT INTO station (station_id, station_name_meteo, station_name_province, station_lat, station_long, station_alias) VALUES (%s, %s, %s, %s,%s,%s)"
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