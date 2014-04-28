import sys
import osr
import math as math
import numpy as np
import gdal
from gdalconst import *
import os
import ntpath
import features
import struct

TO_REFLECTANCE, TO_TEMPERATURE, ORG = range(3)

def deg2rad(deg):
	return (deg * math.pi / 180)

def get_basename(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def create_raster(output_filename, datal, cols, rows, band_type, geotransform, zone=48, hemisphere=1):
	if not os.path.exists(os.path.dirname(output_filename)):
			os.makedirs(os.path.dirname(output_filename))

	driver = gdal.GetDriverByName('GTiff')
	number_of_bands = 1

	srs = osr.SpatialReference()
	srs.SetUTM(zone, hemisphere)
	srs.SetWellKnownGeogCS('WGS84')

	dataset = driver.Create(output_filename, cols, rows, number_of_bands, band_type)
	if dataset is None:
		print "Output dataset is none"
		exit(1)

	# write projection and geo transform metadata
	dataset.SetProjection(srs.ExportToWkt())
	dataset.SetGeoTransform(geotransform)

	band = dataset.GetRasterBand(1)

	# write data to file
	band.WriteArray(datal, 0, 0)
	band.SetNoDataValue(-9999)
	band.FlushCache()

	# clean up
	dataset = None

class SImage(object):
	"""docstring for SImage"""
	def __init__(self, filename):
		super(SImage, self).__init__()
		self.dataset = gdal.Open(filename, GA_ReadOnly)
		if self.dataset is None:
			print 'Couldnt open file'
			exit(1)

		self.geotransform = self.dataset.GetGeoTransform()
		self.invgeotransform = gdal.InvGeoTransform(self.geotransform)[1]
		self.band = self.dataset.GetRasterBand(1)
		self.band_type = self.band.DataType
		self.YSize = self.dataset.RasterYSize
		self.XSize = self.dataset.RasterXSize

	def __del__(self):
		self.dataset = None

	def value_at(self, y, x):
		data = self.band.ReadAsArray(y, x, 1, 1)
		return data[0, 0]
	
	def geo_to_pixel(self, geo_x, geo_y):
		"""geo_x: easting/long, geo_y:northing/lat"""
		if self.dataset is None:
			print 'Couldnt open file'
			return -1, -1

		pixel, line = gdal.ApplyGeoTransform(self.invgeotransform, geo_x, geo_y)
		
		pixel = int(pixel)
		line = int(line)

		return pixel, line

	def pixel_to_geo(self, line = 0, pixel = 0):
		"""geo_x: easting/long, geo_y:northing/lat"""
		if self.dataset is None:
			print 'Couldnt open file'
			return -1, -1

		geo_x, geo_y = gdal.ApplyGeoTransform(self.geotransform, pixel, line)

		return geo_x, geo_y

class Landsat5(SImage):
	"""docstring for Landsat5"""
	def __init__(self, path, LMIN, LMAX, QCALMIN, QCALMAX, ESUN, D, SOLAR_ZEN_ANGLE, K1, K2, epsilon):
		super(Landsat5, self).__init__()
		self.LMIN = LMIN
		self.LMAX = LMAX
		self.QCALMIN = QCALMIN
		self.QCALMAX = QCALMAX
		self.ESUN = ESUN
		self.D = D
		self.SOLAR_ZEN_ANGLE = SOLAR_ZEN_ANGLE
		self.K1 = K1
		self.K2 = K2
		self.epsilon = epsilon

	def _radiance_to_Reflectance(self, radiance):
		return math.pi * radiance * math.pow(self.D, 2) * math.cos(self.SOLAR_ZEN_ANGLE) / self.ESUN

	def _radiance_to_Temperature(self, radiance):
		"""Output temperature unit is Kelvin"""
		return self.K2 / math.log((1 + ((self.K1 * self.epsilon) / radiance)), math.e)

	def _dn_to_Radiance(self, dn):
		return (self.LMAX - self.LMIN) * (dn - self.QCALMIN) / (self.QCALMAX - self.QCALMIN) + self.LMIN

	def _dn_to_Reflectance(self, dn):
		return self._radiance_to_Reflectance(self._dn_to_Radiance(dn))

	def _dn_to_Temperature(self, dn):
		return self._radiance_to_Temperature(self._dn_to_Radiance(dn))

class Landsat8(SImage):
	"""docstring for Landsat8"""
	def __init__(self, path, RADIANCE_MULT_BAND, RADIANCE_ADD_BAND, REFLECTANCE_MULT_BAND, REFLECTANCE_ADD_BAND, SUN_ELEVATION, K1_CONSTANT_BAND=0.0, K2_CONSTANT_BAND=0.0):
		super(Landsat8, self).__init__(path)

		self.RADIANCE_MULT_BAND = RADIANCE_MULT_BAND
		self.RADIANCE_ADD_BAND = RADIANCE_ADD_BAND
		self.REFLECTANCE_MULT_BAND = REFLECTANCE_MULT_BAND
		self.REFLECTANCE_ADD_BAND = REFLECTANCE_ADD_BAND
		self.SUN_ELEVATION = SUN_ELEVATION
		self.K1_CONSTANT_BAND = K1_CONSTANT_BAND
		self.K2_CONSTANT_BAND = K2_CONSTANT_BAND

	def _dn_to_Radiance(self, dn):
		return self.RADIANCE_MULT_BAND * dn + self.RADIANCE_ADD_BAND

	def _dn_to_Reflectance(self, dn):
		uncorrected_reflectance = self.REFLECTANCE_MULT_BAND * dn + self.REFLECTANCE_ADD_BAND
		return uncorrected_reflectance / math.cos(self.SUN_ELEVATION)

	def _dn_to_Temperature(self, dn):
		return self.K2_CONSTANT_BAND / math.log((self.K1_CONSTANT_BAND / _dn_to_Radiance(dn) + 1), math.e)

class Landsat5CloudExtractor(object):
	"""docstring for Landsat"""
	def __init__(self, path):
		super(Landsat, self).__init__()
		self._initialize(path)
	
	def _initialize(self, path):
		basename = os.path.join(path, get_basename(path))
		self.bands = []
		for i in range(1, 8):
			self.bands.append(SImage(basename + "_B{0}.TIF".format(i)))
		
		self.parameters_filename = basename + "_MTL.txt"
		self._read_parameters(parameters_filename)

		self.output_cloud_mask = basename + "_CM.TIF"

	def _read_parameters(self, parameters_filename):
		self.LMIN = np.zeros(7)
		self.LMAX = np.zeros(7)

		self.LMIN[0] = -1.520
		self.LMIN[1] = -2.840
		self.LMIN[2] = -1.170
		self.LMIN[3] = -1.510
		self.LMIN[4] = -0.370
		self.LMIN[5] = 1.238
		self.LMIN[6] = -0.150
		
		self.LMAX[0] = 193.000
		self.LMAX[1] = 365.000
		self.LMAX[2] = 264.000
		self.LMAX[3] = 221.000
		self.LMAX[4] = 30.200
		self.LMAX[5] = 15.303
		self.LMAX[6] = 16.500
		
		self.QCALMIN = 1
		self.QCALMAX = 255

		self.ESUN = np.zeros(7)
		self.ESUN[0] = 1969.000
		self.ESUN[1] = 1840.000
		self.ESUN[2] = 1551.000
		self.ESUN[3] = 1044.000
		self.ESUN[4] = 225.700
		self.ESUN[5] = 82.07
		self.ESUN[6] = 1368.000

		self.D = 0.99359
		self.SOLAR_ZEN_ANGLE = 1

		self.K1 = 607.76
		self.K2 = 1260.56
		self.epsilon = 0.95

	def _create_cloud_mask(self):
		output = open("cloud_mask.txt", "w+")

		cols = self.bands[2].XSize
		rows = self.bands[2].YSize

		datal = np.zeros((rows, cols), dtype=np.int)
		for y in range(0, rows):
			print y * 100.0 / rows, "%"
			for x in range(0, cols):
				SD = 0.03
				cloud_state = features.CL_FREE
				if x > 0 and x < cols - 1 and y > 0 and y < rows - 1:
					windows = [self._dn_to_Reflectance(self.bands[1].value_at(y + i, x + j)) for i in range(-1,2) for j in range(-1, 2)]
					SD = features.standard_deviation(windows)
				if SD > 0.033:
					values = [self._dn_to_Reflectance(self.bands[i].value_at(y, x)) for i in range(0, 7)]
					cloud_state = features.cloud_cover_state(values[0], values[1], values[2], values[3], values[4], values[5], values[6])
				
				output.write("{0}, ".format(cloud_state))
				datal[y][x] = cloud_state
			output.write("\n")
		
		output.close()

		create_raster(self.output_cloud_mask, datal, cols, rows, GDT_Byte, self.bands[1].geotransform)

class Landsat8CloudExtractor(object):
	"""docstring for Landsat8"""
	def __init__(self, path):
		super(Landsat8CloudExtractor, self).__init__()
		self._initialize(path)
		
	def _initialize(self, path):
		basename = os.path.join(path, get_basename(path))
		parameters_filename = basename + "_MTL.in"
		self._read_parameters(parameters_filename)

		self.bands = []
		for i in range(1, 8):
			if i <= 5:
				band_name = basename + "_B{0}C.TIF".format(i+1)
				self.bands.append(Landsat8(band_name, self.RADIANCE_MULT_BAND[i], self.RADIANCE_ADD_BAND[i], self.REFLECTANCE_MULT_BAND[i], self.REFLECTANCE_ADD_BAND[i], self.SUN_ELEVATION, 0, 0))
			if i == 7:
				band_name = basename + "_B{0}C.TIF".format(i)
				self.bands.append(Landsat8(band_name, self.RADIANCE_MULT_BAND[i-1], self.RADIANCE_ADD_BAND[i-1], self.REFLECTANCE_MULT_BAND[i-1], self.REFLECTANCE_ADD_BAND[i-1], self.SUN_ELEVATION, 0, 0))
			if i == 6:
				band_name = basename + "_B{0}C.TIF".format(10)
				self.bands.append(Landsat8(band_name, self.RADIANCE_MULT_BAND[9], self.RADIANCE_ADD_BAND[9], 0, 0, self.SUN_ELEVATION, self.K1_CONSTANT_BAND[0], self.K2_CONSTANT_BAND[0]))

		self.output_cloud_mask = basename + "_CM.TIF"

	def _read_parameters(self, parameters_filename):
		self.SUN_ELEVATION = deg2rad(54.26983268)

		a = np.loadtxt(parameters_filename, dtype='str', delimiter="=")

		self.RADIANCE_MULT_BAND = [float(a[i, 1]) for i in range(0, 11)]
		self.RADIANCE_ADD_BAND = [float(a[i, 1]) for i in range(11, 22)]
		self.REFLECTANCE_MULT_BAND = [float(a[i, 1]) for i in range(22, 31)]
		self.REFLECTANCE_ADD_BAND = [float(a[i, 1]) for i in range(31, 40)]
		self.K1_CONSTANT_BAND = [float(a[i, 1]) for i in range(40, 42)]
		self.K2_CONSTANT_BAND = [float(a[i, 1]) for i in range(42, 44)]

	def _create_cloud_mask(self):
		# output = open("cloud_mask.txt", "w+")

		cols = self.bands[2].XSize
		rows = self.bands[2].YSize

		datal = np.zeros((rows, cols), dtype=np.int)
		for y in range(0, rows):
			print y * 100.0 / rows, "%"
			for x in range(0, cols):
				SD = 0.03
				cloud_state = features.CL_FREE
				# if x > 1 and x < cols - 2 and y > 1 and y < rows - 2:
				# 	windows = [self.bands[1]._dn_to_Reflectance(self.bands[1].value_at(y + i, x + j)) for i in range(-1,2) for j in range(-1, 2)]
				# 	SD = features.standard_deviation(windows)
				# if SD > 0.033:
				if True:
					values = [self.bands[i]._dn_to_Reflectance(self.bands[i].value_at(y,x)) for i in range(0, 7)]
					values[5] = self.bands[5]._dn_to_Radiance(self.bands[5].value_at(y,x))
					
					cloud_state = features.cloud_cover_state(values[0], values[1], values[2], values[3], values[4], values[5], values[6])
				
				# output.write("{0}, ".format(cloud_state))
				datal[y][x] = cloud_state
			# output.write("\n")
		
		# output.close()
		create_raster(self.output_cloud_mask, datal, cols, rows, GDT_Byte, self.bands[2].geotransform)

if __name__ == '__main__':
	image = Landsat8CloudExtractor(sys.argv[1])
	image._create_cloud_mask()