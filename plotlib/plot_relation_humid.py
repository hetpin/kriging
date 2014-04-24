"""
Simple demo with multiple subplots.
"""
import numpy as np
import matplotlib.pyplot as plt
from Utility import haversine
from get_data import getObservationList
from get_dif import getAStationTemp
from get_dif import getAStationHumid
import os.path

x1 = np.linspace(0.0, 5.0)
x2 = np.linspace(0.0, 2.0)
y1 = np.cos(2 * np.pi * x1) * np.exp(-x1)
y2 = np.cos(2 * np.pi * x2)
query_date = '2011-01-02'
list = getObservationList(query_date)
size = len(list)# 98 Tram
item0 = list[0]
list_index = []
list_station_all = [] #98 tram
for x in xrange(1,size+1):
	list_station_all.append(getAStationHumid(str(x)))
	#list_index.append(x)
	#list_h.append(haversine(item0[2], item0[1], list[x][2], list[x][1]))

list_value = []
list_h = []
def calculateOneStation(id):
	item0 = list[id]
	station_0 = list_station_all[id]
	for x in xrange(1,size):
		item = list_station_all[x]
		correlate = np.corrcoef(station_0, item)[0,1]
		list_index.append(x)
		list_value.append(correlate)
		list_h.append(haversine(item0[2], item0[1], list[x][2], list[x][1]))

for x in xrange(0,size):
	calculateOneStation(x)

list_period_value= []
list_period_h = []
d = 50
size_h = len(list_h)
for x in xrange(0,32):
	mean = 0
	total = 0
	for y in xrange(0,size_h):
		if (list_h[y] > d*x) and (list_h[y] < d*(x+1)):
			total = total +1
			mean = mean + list_value[y]
	if total >0:
		list_period_value.append(mean/total)
		list_period_h.append(d*x)

#list_sort = []
#size = len(list_value)
#for x in xrange(1,size):
#	list_sort.append((list_h[x], list_value[x]))

plt.subplot(2, 1, 1)

plt.plot(list_h, list_value, 'r.')
plt.title('A tale of 2 subplots')
plt.ylabel('r')

plt.subplot(2, 1, 2)
plt.plot(list_period_h, list_period_value, 'r.-')
plt.xlabel('Distance (km)')
plt.ylabel('r')
plt.savefig(os.path.splitext(os.path.basename('humid_correlation_all'))[0] + '.png')

plt.show()
