#test with time
#----------------------------- 
# Converting Epoch Seconds to DMYHMS
import datetime, time
from dateutil.relativedelta import relativedelta

EpochSeconds = 568018818
now = datetime.datetime.fromtimestamp(EpochSeconds)
#gmttime = time.gmtime(EpochSeconds)
#or use datetime.datetime.utcfromtimestamp()
print now
#print gmttime
now = now - datetime.timedelta(hours=7) 
now = now + relativedelta(years=23)
#gmttime = gmttime + datetime.timedelta(days=23)
print now
#=> datetime.datetime(2003, 8, 6, 20, 43, 20)
print now.ctime()
#=> Wed Aug  6 20:43:20 2003

