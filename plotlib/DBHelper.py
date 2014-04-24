#insert data to db
import string, sys, os, time
import psycopg2

#Import full (temp, humid, rain)
def insertCorrelationAll(list):
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres') # for default localhost
	    #con = psycopg2.connect(database='fimo_fire', user='uet', password = 'uet123', host = '192.168.3.190', port = 5432) 
	    cur = con.cursor()  
	    query = "INSERT INTO correlation (corr_sta_1, corr_sta_2, corr_temp13, corr_humid13, corr_rain13, corr_rain24) VALUES ( %s, %s, %s,%s,%s,%s)"
	    #print query
	    cur.executemany(query, list)
	    con.commit()
	except psycopg2.DatabaseError, e:
	    if con:
	        con.rollback()
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    if con:
	        con.close()
#Import one att
def insertCorrelationOne(att, list):
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres') # for default localhost
	    #con = psycopg2.connect(database='fimo_fire', user='uet', password = 'uet123', host = '192.168.3.190', port = 5432) 
	    cur = con.cursor()
	    query = "INSERT INTO correlation (corr_sta_1, corr_sta_2, "+att+" ) VALUES ( %s, %s, %s)"
	    #print query
	    cur.executemany(query, list)
	    con.commit()
	except psycopg2.DatabaseError, e:
	    if con:
	        con.rollback()
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    if con:
	        con.close()

#Update one attribute
def updateCorrelationOne(att, list):
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres') # for default localhost
	    #con = psycopg2.connect(database='fimo_fire', user='uet', password = 'uet123', host = '192.168.3.190', port = 5432) 
	    cur = con.cursor()
	    for item in list:
	    	print item
		    query = "UPDATE correlation SET " + att+ "  =%s WHERE corr_sta_1 = %s and corr_sta_1 = %s ", (item[0],item[1], item[2])
			#cur.execute("UPDATE station SET station_lat=%s ,station_long = %s,station_alt =%s WHERE station_id=%s", (item.lat,item.lon, item.alt, item.id))
		    print query
	    con.commit()
	except psycopg2.DatabaseError, e:
	    if con:
	        con.rollback()
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    if con:
	        con.close()

#	for item in list_data:
#		print 'updating ', item.id, item.name_tram 
#		cur.execute("UPDATE station SET station_lat=%s ,station_long = %s,station_alt =%s WHERE station_id=%s", (item.lat,item.lon, item.alt, item.id))
#		con.commit()
#		updated =updated + cur.rowcount
#	print updated

#TEST
list = []
for x in xrange(1,10):
	item = (x,x,x)
	list.append(item)
insertCorrelationOne( 'corr_temp13',list)