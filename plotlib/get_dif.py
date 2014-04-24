# -*- coding: utf-8 -*-
import psycopg2
import psycopg2.extras
from pprint import pprint
def getAStationHumid(station_id):
	#print 'getting ', station_id
	list = []
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres') 
	    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
	    query = "select obs.obs_station_id, obs.obs_humid13 from observation as obs, station as sta where obs.obs_station_id = sta.station_id and obs.obs_station_id = "+ station_id +" order by obs.obs_date"
	    cursor.execute(query)
	    print cursor.rowcount
	    rows = cursor.fetchall()
	    for row in rows:
	    	#item0 for id, item1 for lat, item2 for lon, item3 for temperature value
			item = row["obs_humid13"]# [row["obs_station_id"], row["obs_temp13"]]
			#print item
			list.append(item)
			obs_temp = str(row["obs_humid13"])
			#if float(obs_temp) < 2:
			#	print obs_temp
			#	continue
	except psycopg2.DatabaseError, e:
	    
	    if con:
	        con.rollback()
	    
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    
	    if con:
	        con.close()
	return list
def getAStationTemp(station_id):
	#print 'getting ', station_id
	list = []
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres') 
	    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
	    query = "select obs.obs_station_id, obs.obs_temp13, sta.station_alt from observation as obs, station as sta where obs.obs_station_id = sta.station_id and obs.obs_station_id = "+ station_id +" order by obs.obs_date"
	    cursor.execute(query)
	    print cursor.rowcount
	    rows = cursor.fetchall()
	    for row in rows:
	    	#item0 for id, item1 for lat, item2 for lon, item3 for temperature value
			item = row["obs_temp13"]# [row["obs_station_id"], row["obs_temp13"]]
			#print item
			list.append(item)
			#obs_temp = str(row["obs_temp13"])
			#if float(obs_temp) < 2:
			#	print obs_temp
			#	continue
	except psycopg2.DatabaseError, e:
	    
	    if con:
	        con.rollback()
	    
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    
	    if con:
	        con.close()
	return list
def getAStationTempNormalize(station_id):
	#print 'getting ', station_id
	list = []
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres') 
	    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
	    query = "select obs.obs_station_id, obs.obs_temp13, sta.station_alt from observation as obs, station as sta where obs.obs_station_id = sta.station_id and obs.obs_station_id = "+ station_id +" order by obs.obs_date"
	    cursor.execute(query)
	    print cursor.rowcount
	    rows = cursor.fetchall()
	    for row in rows:
		alt = row["station_alt"]
		item = row["obs_temp13"]
		item = item + 0.6*(alt//100)*100
		#print alt, ' ', (alt//100),' ', 0.6*(alt//100)
		list.append(item)
	except psycopg2.DatabaseError, e:
	    
	    if con:
	        con.rollback()
	    
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    
	    if con:
	        con.close()
	return list
def getAStationRain(station_id):
	#print 'getting ', station_id
	list = []
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres') 
	    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
	    query = "select obs.obs_station_id, obs.obs_rain13 from observation as obs, station as sta where obs.obs_station_id = sta.station_id and obs.obs_station_id = "+ station_id +" order by obs.obs_date"
	    cursor.execute(query)
	    print cursor.rowcount
	    rows = cursor.fetchall()
	    for row in rows:
	    	#item0 for id, item1 for lat, item2 for lon, item3 for temperature value
			item = row["obs_rain13"]# [row["obs_station_id"], row["obs_temp13"]]
			#print item
			list.append(item)
			obs_temp = str(row["obs_rain13"])
			#if float(obs_temp) < 2:
			#	print obs_temp
			#	continue
	except psycopg2.DatabaseError, e:
	    
	    if con:
	        con.rollback()
	    
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    
	    if con:
	        con.close()
	return list

getAStationTemp('1')