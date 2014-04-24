import numpy as np
import matplotlib.pyplot as plt
from get_data import getTempOfAAtationFromTo
import os.path

id1 = 15
id2 = 17
list_value = []
list_time =[]

for x in xrange(2004,2015):
	print x
	date_from = str(x) + '-01-01'
	date_to = str(x) + '-12-30'
	list_1 = getTempOfAAtationFromTo(id1, date_from, date_to)
	list_2 = getTempOfAAtationFromTo(id2, date_from, date_to)
	size1= len(list_1)
	size2= len(list_2)
	print size1,' ', size2
	if size1 == 0:
		continue
	list_1_all = zip(*list_1)
	list_1_temp = list_1_all[3]
	list_1_humid = list_1_all[4]
	list_1_rain = list_1_all[5]
	list_2_all = zip(*list_2)
	list_2_temp = list_2_all[3]
	list_2_humid = list_2_all[4]
	list_2_rain = list_2_all[5]
	#print list_1_temp
	#print list_1_humid
	#print list_1_rain
	correlation = np.corrcoef(list_1_temp, list_2_temp)[0,1]
	list_value.append(correlation)
	list_time.append(x)

#print list_time
#print list_value
plt.subplot(2, 1, 1)

#plt.plot(list_h, list_value, 'r.')
plt.title('A tale of 2 subplots')
plt.ylabel('r')

plt.subplot(2, 1, 2)
plt.plot(list_time, list_value, 'r.--')
plt.xlabel('Distance (km)')
plt.ylabel('r')
plt.ylim([0,1])
plt.xlim([2004,2015])
plt.savefig(os.path.splitext(os.path.basename('correlationTenYearTemp'))[0] + '.png')
plt.show()
