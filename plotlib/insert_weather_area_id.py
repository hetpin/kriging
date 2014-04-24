#Insert weather area id
# -*- coding: utf-8 -*-
import psycopg2
from get_data import getAllObservation
f = open('workfile.txt', 'w')

list_sta = getAllObservation()
list_new = []# This list contain area id
size = len(list_sta)
#IMPORTING
'''
con = None
try:
	con = psycopg2.connect(database='fimo_db', user='postgres')
	updated = 0
	cur = con.cursor()  
	for item in list_data:
		print 'updating ', item.id, item.name_tram 
		cur.execute("UPDATE station SET station_lat=%s ,station_long = %s,station_alt =%s WHERE station_id=%s", (item.lat,item.lon, item.alt, item.id))
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
'''