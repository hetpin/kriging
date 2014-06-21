#test
from setting import *
def printDate():
	print 'in setting test: ', date_to
def changeDate():
	global date_to
	date_to = 'changedDate'
	print date_to
	printDate()
changeDate()