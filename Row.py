class Row(object):
    id = 0
    name_tinh = ""
    name_tram = ""
    temp_13 = 0
    humid_13 = 0
    rain_13 = 0
    rain_24 = 0
    file_name = ""
    lat = 0
    lon = 0
    alt = 0

    # The class "constructor" - It's actually an initializer 
    def __init__(self, id, name_tinh, name_tram, temp_13, humid_13, rain_13, rain_24, file_name, lat, lon, alt):
        self.id = id
        self.name_tinh = name_tinh
        self.name_tram = name_tram
        self.temp_13 = temp_13
        self.humid_13 = humid_13
        self.rain_13 = rain_13
        self.rain_24 = rain_24
        self.file_name = file_name
        self.lat = lat
        self.lon = lon
        self.alt = alt
        
def make_row(id, name_tinh, name_tram, temp_13, humid_13, rain_13, rain_24, file_name, lat, lon, alt):
    row = Row(id, name_tinh, name_tram, temp_13, humid_13, rain_13, rain_24, file_name, lat, lon, alt)
    return row
def __repr__(self):
	return '__repr__'