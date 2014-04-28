import numpy
from osgeo import osr, gdal
minLat = 8.4
maxLat = 23.6
minLon = 102.1
maxLon = 109.8
shift = 0.1
row = int((maxLat-minLat)/shift)
col = int((maxLon-minLon)/shift)

def exportGeotiff(filename, raster, row, col, resolution, minLon, minLat):
	format = "GTiff"
	driver = gdal.GetDriverByName( format )
	dst_ds = driver.Create(filename, col, row, 1, gdal.GDT_Byte )
	'''
	raster = numpy.zeros( (row, col) )
	for x in xrange(10,20):
		for y in xrange(10,20):
			raster[x][y] = 100
	'''
	# top left x, w-e pixel resolution, rotation, top left y, rotation, n-s pixel resolution
	dst_ds.SetGeoTransform( [ minLon, resolution, 0, minLat, 0, resolution ] )
	# set the reference info 
	srs = osr.SpatialReference()
	srs.SetWellKnownGeogCS("WGS84")
	dst_ds.SetProjection( srs.ExportToWkt() )
	dst_ds.GetRasterBand(1).WriteArray(raster)