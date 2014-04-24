# -*- coding: utf-8 -*-
import fileinput
import glob
import string, sys, os, time
import xlrd
import psycopg2
from Row import Row
from pprint import pprint
curr_row = -1
list_root = []
empty_string = '-'
#IMPORTING variable
list_ = []

f = open('workfile.txt', 'w')
def importOneFolder(expression):
	index = 0
	#for line in fileinput.input(glob.glob("data/*.xls")):
	for line in fileinput.input(glob.glob(expression)):
		search = '.xls' #Tim tung thang cho nay//BT010111
		if fileinput.filename().find(search) != -1:
			print '-Start for-'
		else:
			continue
		name = fileinput.filename()
		print name
		shirf = 19#for 2005-2014
		shirf = 19#for 2005-2014
		ngay = name[shirf +0] +name[shirf +1]
		thang = name[shirf +2] + name[shirf +3]
		nam = '20' + name[shirf +4] + name[shirf +5]
		print ngay, thang, nam
		if fileinput.isfirstline(): # first in a file?
			sys.stderr.write("-- reading %s --\n" % fileinput.filename())
		workbook = xlrd.open_workbook(fileinput.filename())
		#worksheet = workbook.sheet_by_name('Sheet1')
		worksheet = workbook.sheet_by_index(0)
		num_rows = worksheet.nrows - 1
		num_cells = worksheet.ncols - 1
		list_data = []
	        #testing purpose
	        curr_row = 1 #start at 1
	        num_rows = 99 #end   at 99
	        while curr_row < num_rows:
				curr_row += 1
				row = worksheet.row(curr_row)
				#print 'Row:', curr_row
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
						cell_value = str(cell_value).replace(" ", "").replace("/","")
						if cell_value == empty_string or cell_value == ' ' or cell_value =='' or str(cell_value).find(empty_string) != -1 :
							row_data.temp_13 = 0
						else:
							row_data.temp_13 = cell_value
						if cell_type == 0:
							row_data.temp_13 = 0
					if curr_cell == 4 :
						cell_value = str(cell_value).replace(" ", "").replace("/","")
						if cell_value == empty_string or cell_value == ' ' or cell_value =='' or str(cell_value).find(empty_string) != -1 :
							row_data.humid_13 = 0
						else:
							row_data.humid_13 = cell_value
						if cell_type == 0:
							row_data.humid_13 = 0
					if curr_cell == 5 :
						cell_value = str(cell_value).replace(" ", "").replace("/","")
						if cell_value == empty_string or cell_value == ' ' or cell_value =='' or str(cell_value).find(empty_string) != -1 :
							row_data.rain_13 = 0
						else:
							row_data.rain_13 = cell_value
						if cell_type == 0:
							row_data.rain_13 = 0						
					if curr_cell == 6 :
						cell_value = str(cell_value).replace(" ", "").replace("/","")
						if cell_value == empty_string or cell_value == ' ' or cell_value =='' or str(cell_value).find(empty_string) != -1 :
							row_data.rain_24 = 0
						else:
							row_data.rain_24 = cell_value
						if cell_type == 0:
							row_data.rain24 = 0
					if curr_cell == 7 :
						row_data.file_name = cell_value
				list_data.append(row_data)
	#	for item in list_data:
	#		pprint (vars(item))
		list_root.append(list_data)
		f.write(fileinput.filename()+ str(index) +'\n')
		print index
		for item in list_data:
			index = index + 1
			if item.rain_24 == '':
				item.rain_24 = 0
			#print str(item.temp_13), str(item.humid_13), str(item.rain_13), str(item.rain_24), item.id 
			list_.append((ngay+ '-'+thang+ '-'+nam, float(str(item.temp_13).replace(',','.')), float(str(item.humid_13).replace(',','.')), float(str(item.rain_13).replace(',','.')), float(str(item.rain_24).replace(',','.')), item.id))
			#test = (ngay+ '-'+thang+ '-'+nam, item.temp_13, item.humid_13, item.rain_13, item.rain_24, item.id)
			#print test
			#time.sleep(5.5) 

#done 14/13/12/11/10/09/08/07/06/05
for x in xrange(2014,2015):
	#"data/*.xls"
	expression = "data/all/nam" +str(x)+"/*.xls"
	print expression
	importOneFolder(expression)
con = None
try:
    con = psycopg2.connect(database='fimo_db', user='postgres') # for default localhost
    #con = psycopg2.connect(database='fimo_fire', user='uet', password = 'uet123', host = '192.168.3.190', port = 5432) 
  
    cur = con.cursor()  
    
#    cur.execute("DROP TABLE IF EXISTS cars")
#    cur.execute("CREATE TABLE cars(id INT PRIMARY KEY, name TEXT, price INT)")
#    query = "INSERT INTO observation (obs_id, obs_date, obs_temp13, obs_humid13, obs_rain13, obs_rain24, obs_station_id) VALUES (%s, %s, %s, %s,%s,%s,%s)"
    query = "INSERT INTO observation (obs_date, obs_temp13, obs_humid13, obs_rain13, obs_rain24, obs_station_id) VALUES ( %s, %s, %s,%s,%s,%s)"
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