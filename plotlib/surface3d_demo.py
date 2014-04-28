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
	#R = np.sqrt(X**2 + Y**2)
	#Z = np.sin(R)
	Z = curve[0]*X +curve[1]*Y +curve[2]
	#Z = getTrendValue(curve, X, Y)
	surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm,
	        linewidth=0, antialiased=False)
	ax.scatter(xs, ys, zs, c='g', marker='o')
	#ax.set_zlim(-1.01, 1.01)

	#ax.zaxis.set_major_locator(LinearLocator(10))
	#ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

	fig.colorbar(surf, shrink=0.5, aspect=5)

	plt.show()
'''
curve = [1,10,-3]
plotSurface(curve)
'''