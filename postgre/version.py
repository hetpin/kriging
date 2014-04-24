#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import sys


con = None

try:
     
    #con = psycopg2.connect(database='fimo_db', user='postgres') # for default localhost
    con = psycopg2.connect(database='fimo_fire', user='uet', password = 'uet123', host = '192.168.3.190', port = 5432) 
    cur = con.cursor()
    cur.execute('SELECT version()')          
    ver = cur.fetchone()
    print ver    
    

except psycopg2.DatabaseError, e:
    print 'Error %s' % e    
    sys.exit(1)
    
    
finally:
    
    if con:
        con.close()