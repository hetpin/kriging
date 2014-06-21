from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt
import numpy as np
from Utility import getTrendValue
minLat = 8.4
maxLat = 23.4
minLon = 102.1
maxLon = 109.4

def plotSurface(curve, list_points):
	list_ele = zip(*list_points)
	xs = list_ele[0]
	ys = list_ele[1]
	zs = list_ele[2]
	fig = plt.figure()
	ax = fig.gca(projection='3d')
	X = np.arange(minLat, maxLat, 0.5)
	Y = np.arange(minLon, maxLon, 0.5)
	X, Y = np.meshgrid(X, Y)
	Z = curve[0]*X +curve[1]*Y +curve[2]
	#Z = getTrendValue(curve, X, Y)
	surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm,
	        linewidth=0, antialiased=False)
	#for i in xrange(1,len(xs)):
	#	print xs[i], ys[i], zs[i]
	ax.scatter(xs, ys, zs, c='g', marker='o')

	fig.colorbar(surf, shrink=0.5, aspect=5)
	print len(list_points)
	print curve
	plt.show()
'''
z = ax + by +c
cruve = [a, b, c]
curve = [1,10,-3]
plotSurface(curve)
'''