# -*- coding: utf-8 -*-
import datetime
import fileinput
import glob
import string, sys
import xlrd
import psycopg2
import psycopg2.extras
from Row import Row
from pprint import pprint
curr_row = -1
list_root = []
empty_string = '-'
#IMPORTING variable
list_ = []
index = 0
f = open('workfile_humid.txt', 'w')
con = None
try:
    con = psycopg2.connect(database='fimo_db', user='postgres') 
    cursor = con.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = 'select ter.terra_humid, ter.terra_date, obs.obs_station_id, obs.obs_humid13, ter.terra_time from terra as ter, observation as obs' 
    query = query + " where ter.terra_station_id = obs.obs_station_id and ter.terra_date = obs.obs_date and ter.terra_time::time > '09:00:00' and ter.terra_time::time < '17:00:00' "
    cursor.execute(query)

    print cursor.rowcount
    rows = cursor.fetchall()
    for row in rows:
		print "%s %s %s %s" % (row["obs_station_id"], row["terra_humid"], row["obs_humid13"], row["terra_time"])
		station_id = str(row["obs_station_id"])
		terra_humid = str(row["terra_humid"])
		obs_humid13 = str(row["obs_humid13"])
#		if float(obs_temp) < 2:
#			print obs_temp
#			continue
		f.write(station_id +'; ' + terra_humid + '; ' + obs_humid13 + '\n');
except psycopg2.DatabaseError, e:
    
    if con:
        con.rollback()
    
    print 'Error %s' % e    
    sys.exit(1)
    
    
finally:
    
    if con:
        con.close()