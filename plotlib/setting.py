#SETTING VARIABLES
#SETTING
LOG = True #Set True to log all and show diagram
isCrossValidation = False
MATRIX_SIZE = 100
LAT_MIN = 8.4
LAT_MAX = 23.6
LON_MIN = 102.1
LON_MAX = 109.8
minLat = 8.4
maxLat = 23.6
minLon = 102.1
maxLon = 109.8
shift = 0.1
row = int((maxLat-minLat)/shift)
col = int((maxLon-minLon)/shift)
date_from= '2011-08-01' # for all pairs
date_to = '2011-08-28'  # for all pairs
#date_from= '2011-01-01'
#date_to = '2011-01-15'
neighbor = 10
DISTANCE_BOUND = 200
FOLD = 5


