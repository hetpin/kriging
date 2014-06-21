#Runvalidation
import datetime
from setting import *
from UniversalKrigingOneModel import start
#Change setting for cross validation
year = 2011
month = 11
day = 11
num_testday = 30
date = datetime.date(year, month, day)#year, month, day
for i in xrange(0,num_testday):
	date_to = date.strftime('%Y-%m-%d')
	date_from = (date - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
	print date_from, date_to
	start(date_from, date_to, isCrossValidation)
	date += datetime.timedelta(days=1)
