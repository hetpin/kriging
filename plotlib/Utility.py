from math import radians, cos, sin, asin, sqrt
import math, time
import numpy as np
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    #print 'from ', lat1, ' ', lon1, ' to ', lat2, ' ', lon2
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    #lon1, lat1, lon2, lat2 = map(radians, [lat1, lon1, lat2, lon2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 

    # 6367 km is the radius of the Earth
    km = 6367 * c
    return km

def distance(lat1, lon1, lat2, lon2):
    radius = 6371 # km

    dlat = math.radians(lat2-lat1)
    dlon = math.radians(lon2-lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = radius * c
    return d
def covariance(x, y):
	size = len(x)
	meanx = sum(x)/size
	meany = sum(y)/size
	cov = 0
	for i in xrange(0,size):
		cov = cov + (x[i]-meanx)*(y[i]-meany)
	cov = cov/(size-1)
	return cov
def semivariance(x, y):
	#print x
	#print y 
	size = len(x)
	semi = 0
	for i in xrange(0,size):
		semi = semi + (x[i] - y[i])*(x[i] - y[i])
	semi = semi/(2*size)
	#print 'n=', size, 'semi=',semi 
	#time.sleep(1)
	return semi
#Optimize c0, a0 for fitting model
#SELECT gid
#FROM vnm_adm1
#WHERE ST_Contains(geom, ST_SetSRID(ST_Point(105.1043443253471, 21.3150676015829),4326))
#Optimize the fitting function with type fct
#x: list of distance
#y: list of semi value
def opt( fct, x, y, parameterRange=None, meshSize=1000 ):
    #Initialize range
    sill = 0.95*max(y)
    if parameterRange == None:
        parameterRange = [ x[1], x[-1] ]
	#Initialize mse array    
    mse = np.zeros( meshSize )
	#create a list of uniform distribution from min to max
    a = np.linspace( parameterRange[0], parameterRange[1], meshSize )
    #Try each a[i]
    for i in range( meshSize ):
    	for j in xrange(len(y)):
	    mse[i] = mse[i] + ( y[j] - spherical( x[j], a[i] ,sill) )**2.0
	mse[i] = mse[i]/len(y)
    #mse[i] = np.mean( ( y - spherical( x, a[i] ,sill) )**2.0 )
    #print 'MIN MSE inside opt =', min(mse)
    return a[ mse.argmin() ], sill, min(mse)
#SPERICAL 
#a0: The hien do nghieng cua ham spherical
#c0: Sill value ~95% max semi value
def spherical(h, a0, c0):
	if h > a0:
		return c0
	else:
		item = h/a0
		return c0*(1.5*item-0.5*(item**3))
def genFitting(h, y, level):
	'''
	return f, mse
	'''
		#FIT ham bac 2
	z = np.poly1d(np.polyfit(h, y, level))
	mse = 0
	for i in xrange(len(y)):
		mse = mse+ ( y[i] - z(h[i]))**2.0
	print 'Ham bac ', level, ': ', z, 'mse= ', mse
	return z, mse
def semiToCov(h, a0, c0):
	return c0 - spherical(h, a0, c0)