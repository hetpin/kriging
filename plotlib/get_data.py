# -*- coding: utf-8 -*-
import psycopg2, time, sys
import psycopg2.extras
from pprint import pprint
from setting import *

#Setting for switch table of terra
table_terra = 'terra'
#table_terra = 'terra_2'

def getObservationList(query_date):
	list = []
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres') 
	    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
	    query = "select sta.station_id ,sta.station_lat, sta.station_long, obs.obs_temp13 from observation as obs, station as sta where obs.obs_station_id = sta.station_id and obs.obs_date = "+"'"+query_date+"%'"
	    cursor.execute(query)
	    print cursor.rowcount
	    rows = cursor.fetchall()
	    for row in rows:
	    	#item0 for id, item1 for lat, item2 for lon, item3 for temperature value
			item = [row["station_id"], row["station_lat"], row["station_long"], row["obs_temp13"]]
			#print item
			list.append(item)
			obs_temp = str(row["obs_temp13"])
			if float(obs_temp) < 2:
				print obs_temp
				continue
	except psycopg2.DatabaseError, e:
	    
	    if con:
	        con.rollback()
	    
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    
	    if con:
	        con.close()
	return list
def getObservationListHumid(query_date):
	list = []
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres') 
	    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
	    query = "select sta.station_id ,sta.station_lat, sta.station_long, obs.obs_humid13 from observation as obs, station as sta where obs.obs_station_id = sta.station_id and obs.obs_date = "+"'"+query_date+"%'"
	    cursor.execute(query)
	    print cursor.rowcount
	    rows = cursor.fetchall()
	    for row in rows:
	    	#item0 for id, item1 for lat, item2 for lon, item3 for temperature value
			item = [row["station_id"], row["station_lat"], row["station_long"], row["obs_humid13"]]
			#print item
			list.append(item)
			obs_temp = str(row["obs_humid13"])
			if float(obs_temp) < 2:
				print obs_temp
				continue
	except psycopg2.DatabaseError, e:
	    
	    if con:
	        con.rollback()
	    
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    
	    if con:
	        con.close()
	return list
def getObservationListRain(query_date):
	list = []
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres') 
	    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
	    query = "select sta.station_id ,sta.station_lat, sta.station_long, obs.obs_rain13 from observation as obs, station as sta where obs.obs_station_id = sta.station_id and obs.obs_date = "+"'"+query_date+"%'"
	    cursor.execute(query)
	    print cursor.rowcount
	    rows = cursor.fetchall()
	    for row in rows:
	    	#item0 for id, item1 for lat, item2 for lon, item3 for temperature value
			item = [row["station_id"], row["station_lat"], row["station_long"], row["obs_temp13"]]
			#print item
			list.append(item)
			obs_temp = str(row["obs_rain13"])
			if float(obs_temp) < 2:
				print obs_temp
				continue
	except psycopg2.DatabaseError, e:
	    
	    if con:
	        con.rollback()
	    
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    
	    if con:
	        con.close()
	return list
def getTempOfAAtationFromTo(station_id, date_from, date_to):
	#print 'geting data of ', station_id, ' from ', date_from, ' to ', date_to
	list = []
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres') 
	    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
	    query = "select sta.station_id ,sta.station_lat, sta.station_long, obs.obs_temp13,obs_humid13,obs_rain13,obs.obs_date, sta.station_alt from observation as obs, station as sta where obs.obs_station_id = sta.station_id and obs.obs_date >= "+"'"+date_from+"'" + " and " +"obs.obs_date <= "+"'"+date_to+"'" + " and " +"obs.obs_station_id = "+ str(station_id) +" order by obs.obs_date"
	    #print query
	    cursor.execute(query)
	    #print cursor.rowcount
	    rows = cursor.fetchall()
	    for row in rows:
			alt = row["station_alt"]
			temp13 = row["obs_temp13"]
			#print alt
			#print temp13
			
			temp13 = temp13 + 0.64*(alt/100) #for normalize by alt
			
			#print temp13
			#time.sleep(1)
	    	#item0 for id, item1 for lat, item2 for lon, item3 for temperature value
			item = [row["station_id"], row["station_lat"], row["station_long"], temp13, row["obs_humid13"], row["obs_rain13"], str(row["obs_date"])]
			#print item
			list.append(item)
			obs_temp = str(row["obs_temp13"])
			if float(obs_temp) < 2:
				#print obs_temp
				continue
	except psycopg2.DatabaseError, e:
	    
	    if con:
	        con.rollback()
	    
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    
	    if con:
	        con.close()
	return list
def getTempOfAAtationADay(station_id, track_date):
	#print 'geting data of ', station_id, ' from ', date_from, ' to ', date_to
	list = []
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres') 
	    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
	    query = "select sta.station_id ,sta.station_lat, sta.station_long, obs.obs_temp13,obs_humid13,obs_rain13,obs.obs_date, sta.station_alt from observation as obs, station as sta where obs.obs_station_id = sta.station_id and obs.obs_date = "+"'"+track_date+"'" + " and " +"obs.obs_station_id = "+ str(station_id) +" order by obs.obs_date"
	    #print query
	    cursor.execute(query)
	    #print cursor.rowcount
	    rows = cursor.fetchall()
	    for row in rows:
			alt = row["station_alt"]
			temp13 = row["obs_temp13"]
			#print alt
			#print temp13
			
			#temp13 = temp13 + 0.6*(alt//100) #for normalize by alt
			
			#print temp13
			#time.sleep(1)
	    	#item0 for id, item1 for lat, item2 for lon, item3 for temperature value
			item = [row["station_id"], row["station_lat"], row["station_long"], alt, temp13, row["obs_humid13"], row["obs_rain13"], str(row["obs_date"])]
			#print item
			list.append(item)
			obs_temp = str(row["obs_temp13"])
			if float(obs_temp) < 2:
				#print obs_temp
				continue
	except psycopg2.DatabaseError, e:
	    
	    if con:
	        con.rollback()
	    
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    
	    if con:
	        con.close()
	if len(list) != 0:
		return list[0]
	else:
		return list
#Get all Station
def getAllObservation():
	list = []
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres') 
	    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
	    query = "select sta.station_id ,sta.station_lat, sta.station_long, sta.station_area_id, sta.station_alt from station as sta order by sta.station_id"
	    cursor.execute(query)
	    #print cursor.rowcount
	    rows = cursor.fetchall()
	    for row in rows:
			item = [row["station_id"], row["station_lat"], row["station_long"], row["station_area_id"], row["station_alt"]]
			if row["station_area_id"] == 2:
				item[3] = 7
			if row["station_id"] == 98:
				continue
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
#Get all stations by area id
def getAllStaByAreaId(area_id):
	list = []
	con = None
	try:
	    con = psycopg2.connect(database='fimo_db', user='postgres') 
	    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
	    query = ""
	    if area_id == 7:# Song hong ghep voi Tay Bac 
		    query = "select sta.station_id ,sta.station_lat, sta.station_long from station as sta where sta.station_area_id =" + str(area_id)+" or sta.station_area_id = 2  order by sta.station_id"
	    else:
			query = "select sta.station_id ,sta.station_lat, sta.station_long from station as sta where sta.station_area_id =" + str(area_id)+" order by sta.station_id"
	    cursor.execute(query)
	    print 'Got ' ,cursor.rowcount, ' for area_id ', area_id
	    rows = cursor.fetchall()
	    for row in rows:
			item = [row["station_id"], row["station_lat"], row["station_long"]]
			#print item
			if row["station_id"] == 98:
				continue
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

def getAreaIdFromLatlon(list_point):
	#SELECT gid FROM vnm_adm1 WHERE ST_Contains(geom, ST_SetSRID(ST_Point(105.1043443253471, 21.3150676015829),4326))
	list_result = []
	list_id = []
	con = None
	try:
	    #con = psycopg2.connect(database='fimo_db', user='postgres')
	    con = psycopg2.connect(database='spatial_db', user='uet', password = 'uet123', host = '192.168.0.96', port = 5432) 
	    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
	    for point in list_point:    	
		    query = "SELECT gid, name_1, varname_1 FROM vnm_adm1 WHERE ST_Contains(geom, ST_SetSRID(ST_Point("+str(point[2])+","+ str(point[1])+"),4326))"
		    cursor.execute(query)
		    rows = cursor.fetchall()
		    for row in rows:
				item = [ point[0], row["gid"], row["varname_1"], row["name_1"]]
				#print str(point[0]), str(row["gid"])
				list_result.append(item)
				list_id.append(row["gid"])
				break
	except psycopg2.DatabaseError, e:
	    
	    if con:
	        con.rollback()
	    
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    
	    if con:
	        con.close()
	for x in xrange(1,9):
		print x, ' ', list_id.count(x)
	return list_result
#get area id from a point(lat, lon)
def getAreaIdFromPoint(point):
	#SELECT gid FROM vnm_adm1 WHERE ST_Contains(geom, ST_SetSRID(ST_Point(105.1043443253471, 21.3150676015829),4326))
	item = [0, 'name_en', 'name_vi']
	con = None
	try:
		#con = psycopg2.connect(database='fimo_db', user='postgres')
		con = psycopg2.connect(database='spatial_db', user='uet', password = 'uet123', host = '192.168.0.96', port = 5432) 
		cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
		query = "SELECT gid, name_1, varname_1 FROM vnm_adm1 WHERE ST_Contains(geom, ST_SetSRID(ST_Point("+str(point[1])+","+ str(point[0])+"),4326))"
		cursor.execute(query)
		rows = cursor.fetchall()
		for row in rows:
			item = [ row["gid"], row["varname_1"], row["name_1"]]
			if row["gid"] == 2:
				item[0] = 7
			#print item
			break
	except psycopg2.DatabaseError, e:
	    
	    if con:
	        con.rollback()
	    
	    print 'Error %s' % e    
	    sys.exit(1)
	finally:
	    
	    if con:
	        con.close()
	return item
#Update areaId: list of item (sta_id, area_id, name_en, name_vi)
def updateAreaIdForSta(list_data):
	con = None
	try:
		#con = psycopg2.connect(database='fimo_db', user='postgres')
		con = psycopg2.connect(database='fimo_fire', user='uet', password = 'uet123', host = '192.168.0.96', port = 5432) 
		updated = 0
		cur = con.cursor()  
		for item in list_data:
			print item
			#print 'updating sta_id', item[0], item[1], item[2], item[3] 
			cur.execute("UPDATE station SET station_area_id=%s ,station_area_name_en = %s,station_area_name_vi =%s WHERE station_id=%s", (item[1],item[2], item[3], item[0]))
			#Uncoment the bellow line to update db
			#con.commit()
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
#Check a point in Vietnam or not : Point(lat, lon)
def isInVietnam(point):
	result = True
	con = None
	try:
		#con = psycopg2.connect(database='fimo_db', user='postgres')
		con = psycopg2.connect(database='spatial_db', user='uet', password = 'uet123', host = '192.168.0.96', port = 5432) 
		cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
		query = "SELECT gid FROM vnm_adm0 WHERE ST_Contains(geom, ST_SetSRID(ST_Point("+str(point[1])+","+ str(point[0])+"),4326))"
		cursor.execute(query)
		if cursor.rowcount == 0:
			result = False
	except psycopg2.DatabaseError, e:
		if con:
			con.rollback()
		print 'Error %s' % e    
		sys.exit(1)
	finally:
		if con:
			con.close()
	return result
#Get all pair: Terra-Observation
#Return list of item [station_id, terra_temp, obs_temp, terra_date, obs_time]
def getTerraObsPairs():
	list = []
	con = None
	try:
		con = psycopg2.connect(database='fimo_db', user='postgres') 
		cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
		query = 'select obs.obs_station_id, ter.terra_temp, obs.obs_temp13, ter.terra_date, ter.terra_time from ' +table_terra+' as ter, observation as obs' 
		query = query + " where ter.terra_station_id = obs.obs_station_id and ter.terra_date = obs.obs_date and ter.terra_time::time > '09:00:00' and ter.terra_time::time < '17:00:00' "
		cursor.execute(query)
		print 'Got ' ,cursor.rowcount, 'pair (Terra-Obs)'
		rows = cursor.fetchall()
		for row in rows:
			item = [row["obs_station_id"], row["terra_temp"], row["obs_temp13"], row["terra_date"], row["terra_time"]]
			#print item
			if row["obs_station_id"] == 98:
				continue
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
def getAvgAllStationAllTime():
	list = []
	con = None
	try:
		con = psycopg2.connect(database='fimo_db', user='postgres') 
		cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
		query = 'select obs.obs_station_id as id, avg(sta.station_lat) as lat, avg(sta.station_long) as lon, avg(obs.obs_temp13) as avg ' 
		query = query + " from observation as obs, station as sta where obs.obs_station_id = sta.station_id group by obs_station_id order by obs.obs_station_id "
		cursor.execute(query)
		print 'Got ' ,cursor.rowcount, ' station average'
		rows = cursor.fetchall()
		for row in rows:
			item = [row["id"], row["lat"], row["lon"], row["avg"]]
			#print item
			if row["id"] == 98:
				continue
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
#Get avg temp of all station in a month, every year.
def getAvgAllStationAMonth(month):
	list = []
	con = None
	try:
		con = psycopg2.connect(database='fimo_db', user='postgres') 
		cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
		query = 'select obs.obs_station_id as id, avg(sta.station_lat) as lat, avg(sta.station_long) as lon, avg(obs.obs_temp13) as avg from observation as obs, station as sta '
		query = query + 'where obs.obs_station_id = sta.station_id and extract(month from obs.obs_date) = '+ str(month) + ' group by obs_station_id order by obs.obs_station_id'
		cursor.execute(query)
		print 'Got ' ,cursor.rowcount, ' station average'
		rows = cursor.fetchall()
		for row in rows:
			item = [row["id"], row["lat"], row["lon"], row["avg"]]
			#print item
			if row["id"] == 98:
				continue
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

#BUGGY function	
def getAvgAllStation(date_from, date_to):
	list = []
	con = None
	try:
		con = psycopg2.connect(database='fimo_db', user='postgres') 
		cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
		query = 'select obs.obs_station_id as id, avg(sta.station_lat) as lat, avg(sta.station_long) as lon, avg(obs.obs_temp13) as avg ' 
		query = query + " from observation as obs, station as sta where obs.obs_station_id = sta.station_id and obs.obs_date >= "+"'"+date_from+"'" + " and " +"obs.obs_date <= "+"'"+date_to+"'"
		+" group by obs_station_id order by obs.obs_station_id "
		print query
		cursor.execute(query)
		print 'Got ' ,cursor.rowcount, ' station average'
		rows = cursor.fetchall()
		for row in rows:
			item = [row["id"], row["lat"], row["lon"], row["avg"]]
			#print item
			if row["id"] == 98:
				continue
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
#Get Satelite data of a day: Temp +- 4 hours
def getSateliteADay(date):
	list = []
	con = None
	try:
		con = psycopg2.connect(database='fimo_db', user='postgres') 
		cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
		query = "select station_id, station_lat, station_long, station_alt, ter.terra_temp, ter.terra_humid, ter.terra_rain from "+table_terra+" as ter, station as sta "
		query = query + "where ter.terra_station_id = sta.station_id and ter.terra_date = '" + date +"' and ter.terra_time::time > '09:00:00' and ter.terra_time::time < '17:00:00'"
		query = query + " order by terra_station_id"
		cursor.execute(query)
		print 'Got ' ,cursor.rowcount, 'Satelite data for ', date
		rows = cursor.fetchall()
		# station_id, lat, lon, alt, temp, humid, rain 
		for row in rows:
			item = [row["station_id"], row["station_lat"], row["station_long"], row["station_alt"], row["terra_temp"], row["terra_humid"], row["terra_rain"]]
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
#getAvgAllStationAMonth(3)
#getAvgAllStation("2011-03-01", "2011-03-30")

#result = getAllStaByAreaId(1)
#print result
#result = getAreaIdFromLatlon(getAllObservation())
#updateAreaIdForSta(result)

#item = getAreaIdFromPoint([21, 105])
#print item
#print result
#getAllObservation()
#getObservationList('2011-01-02')
#getTempOfAAtationFromTo(1, '2011-01-02', '2011-01-10')

#print isInVietnam([21, 105])
#print getTempOfAAtationADay(1, '2011-11-10')
#getTerraObsPairs()

#FOR MOISETURE
def moiseture_getTerraObsPairs():
	list = []
	con = None
	try:
		con = psycopg2.connect(database='fimo_db', user='postgres') 
		cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
		query = 'select obs.obs_station_id, ter.terra_humid, obs.obs_humid13, ter.terra_date, ter.terra_time from '+table_terra+' as ter, observation as obs' 
		query = query + " where ter.terra_station_id = obs.obs_station_id and ter.terra_date = obs.obs_date and ter.terra_time::time > '09:00:00' and ter.terra_time::time < '17:00:00' "
		cursor.execute(query)
		print 'Got ' ,cursor.rowcount, 'pair (Terra-Moisture-Obs)'
		rows = cursor.fetchall()
		for row in rows:
			item = [row["obs_station_id"], row["terra_humid"], row["obs_humid13"], row["terra_date"], row["terra_time"]]
			#print item
			if row["obs_station_id"] == 98:
				continue
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
