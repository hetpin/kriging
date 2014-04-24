import fileinput
import glob
import string, sys
import xlrd
from Row import Row
from pprint import pprint
workbook = xlrd.open_workbook('data/BT311211.xls')
worksheet = workbook.sheet_by_name('Sheet1')
num_rows = worksheet.nrows - 1
num_cells = worksheet.ncols - 1
curr_row = -1
list_data = []
empty_string = '-'

#testing purpose
curr_row = 1 #start at 1
num_rows = 4 #end   at 99

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

for item in list_data:
	pprint (vars(item))