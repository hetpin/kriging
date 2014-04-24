#http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/
#http://www.islascruz.org/html/index.php/blog/show/Get-attachments-with-Python-over-IMAP.html
import imaplib
import email
import datetime
import time

mail = imaplib.IMAP4_SSL('imap.gmail.com')
username = 'ongiavotu@gmail.com'
password = 'thanhhuongthanh'
sender = 'ongiavotu@gmail.com'
header = 'TEST EMAIL'
time_period = 20
mail.login(username, password)
## Star loop ##
while True:
    ### Show today's date and time ##
	print "Current date & time " + time.strftime("%c")
	mail.list()
	# Out: list of "folders" aka labels in gmail.
	mail.select("inbox") # connect to inbox.
	date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
	#result, data = mail.uid('search', None, '(SENTSINCE {date})'.format(date=date))
	search_str = '(SENTSINCE {date} HEADER Subject "{header}" FROM "{sender}" UNSEEN)'.format(date=date, header = header,sender=sender)
	result, data = mail.uid('search', None, search_str)
	if len(data[0])>0:
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
			
	#### Delay for time_period seconds ####
        time.sleep(time_period)
mail.close()
mail.logout()

