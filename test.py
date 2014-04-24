# -*- coding: utf-8 -*-
import fileinput
import glob
import string, sys
import xlrd
from Row import Row
from pprint import pprint
curr_row = -1
list_root = []
empty_string = '-'


for line in fileinput.input(glob.glob("data/*.xls")):
	search = '1011.xls' #Tim tung thang cho nay
	search_tram = 'Muong Te'
	search_tram_list = ['Muong Te', 'Dien Bien', 'Moc Chau', 'Bac Ha','Hoi Xuan','Nam Dong','Tuy Hoa', 'Play Cu', 'Tan Son Nhat', 'TP Ca Mau', 'Chau Doc']
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
			#print 'Row:', curr_row
			curr_cell = -1
			row_data  = Row(curr_row, "name_tinh", "name_tram", 13, 23, 33, 43,"file_name")
			while curr_cell < num_cells:
				curr_cell += 1
				# Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
				cell_type = worksheet.cell_type(curr_row, curr_cell)
				cell_value = worksheet.cell_value(curr_row, curr_cell)
				#print '	', curr_cell, ':', cell_type, ':', cell_value
				if curr_cell == 0 :
					row_data.id = cell_value
				if curr_cell == 1 :
					row_data.name_tinh = cell_value
				if curr_cell == 2 :
					row_data.name_tram = cell_value
				if curr_cell == 3 :
					if cell_value == empty_string:
						row_data.temp_13 = 0
					else:
						row_data.temp_13 = cell_value
#					if row_data.name_tram == search_tram:
#						pprint (vars(row_data))
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
			if row_data.name_tram in search_tram_list:
#				print row_data.name_tram, row_data.temp_13
				list_data.append(row_data)
#			if row_data.name_tram == search_tram:
#				list_data.append(row_data)
	#Print list_data
	#for item in list_data:
	#	pprint (vars(item))
	list_root.append(list_data)
total_temp_list = [0 for i in range(len(search_tram_list))] # Contain all total temperature of ten Tram
for item_list in list_root:
	for i in xrange(0,len(search_tram_list)):
		#print item_list[i].name_tram, item_list[i].temp_13
		total_temp_list[i] = total_temp_list[i] + item_list[i].temp_13
		#for testing one tram
#		if item_list[i].name_tram == 'Huong Khe':
#			print 'Huong Khe', item_list[i].temp_13	
print '' 
print len(list_root), 'ngay cua thang', search
print ''
for i in xrange(0,len(search_tram_list) ):
	print 'Tb ', search_tram_list[i], ' = ', total_temp_list[i]/len(list_root)


