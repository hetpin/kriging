#check email with fucntions
#http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
#http://www.islascruz.org/html/index.php/blog/show/Get-attachments-with-Python-over-IMAP.html
import imaplib
import email
import datetime
import time
from time import gmtime, strftime
import shutil
import fileinput
import glob
import os
import subprocess

mail = imaplib.IMAP4_SSL('imap.gmail.com')
username = 'fimo.uet@gmail.com'
password = 'Fimoadmin135'
sender = 'ongiavotu@gmail.com'
header = 'NEW DATA'
time_period = 20

def importObservationFile(name):
	name = fileinput.filename()
	print name
	ngay = name[7] +name[8]
	thang = name[9] + name[10]
	nam = '20' + name[11] + name[12]
	print ngay, thang, nam
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
		list_.append((index, ngay+ '-'+thang+ '-'+nam, item.temp_13, item.humid_13, item.rain_13, item.rain_24, item.id))

def checkmail(username):
	new_mail = False
	print 'checking ', username
	#print "Current date & time " + time.strftime("%c")
	mail.list()
	# Out: list of "folders" aka labels in gmail.
	mail.select("inbox") # connect to inbox.
	date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
	#result, data = mail.uid('search', None, '(SENTSINCE {date})'.format(date=date))
	search_str = '(SENTSINCE {date} HEADER Subject "{header}" FROM "{sender}" UNSEEN)'.format(date=date, header = header,sender=sender)
	result, data = mail.uid('search', None, search_str)
	if len(data[0])>0:
		new_mail = True
		latest_email_uid = data[0].split()[-1]
		result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
		raw_email = data[0][1]
		email_message = email.message_from_string(raw_email) 
		#print email_message['To']
		print email.utils.parseaddr(email_message['From']) # for parsing "Yuji Tomita" <yuji@grovemade.com>
		#print email_message.items() # print all headers
		for part in email_message.walk():
			if part.get_content_maintype() == 'multipart':
				continue
			if part.get('Content-Disposition') is None:
				continue
			filename = part.get_filename()
			data = part.get_payload(decode=True)
			if not data:
				continue
			f  = open(filename, 'w')
			f.write(data)
			f.close()
	else: 
		print 'NO NEW EMAIL FROM ' + sender
	return new_mail
#Main FLOW
#mail.login(username, password)
#while True:
#	if checkmail(username):
#		print 'Import data'
#	time.sleep(time_period)
#mail.close()
#mail.logout()
f = open('log/log.txt', 'a')
#Download files, then process
src = "downloaded_files"
des = "backup_files"
successed = "processed_files"
listOfFiles = os.listdir(src)
for s in listOfFiles:
	try:
		if s.find(".xls") != -1:
			f.write(strftime("%H:%M:%S %d-%m-%Y : ", gmtime()) + "Processing "+ s +"\n")
			shutil.copy(src+"/"+s, successed+"/"+s)
		else:
			f.write(strftime("%H:%M:%S %d-%m-%Y : ", gmtime()) + "Skip "+ s +"\n")
		f.write(strftime("%H:%M:%S %d-%m-%Y : ", gmtime()) + "Move to backup folder "+ s +"\n")
		shutil.move(src+"/"+s, des)
	except IOError:
		f.write(strftime("%H:%M:%S %d-%m-%Y : ", gmtime()) + 'Fail to move file' +"\n")
		print 'error'
#Run R Script
pathToRScript = 'C:/Program Files/R/R-3.0.2/bin/Rscript.exe'
pathToRFile = 'C:/xampp/htdocs/firer/fetch_gmail/RScript/script_1.R'
proc = subprocess.Popen([pathToRScript,pathToRFile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
return_code = proc.wait()
#stdout, stderr = proc.communicate()

f.close()
print 'EXIT'
# Read from pipes
for line in proc.stdout:
    print("stdout: " + line.rstrip())
for line in proc.stderr:
    print("stderr: " + line.rstrip())