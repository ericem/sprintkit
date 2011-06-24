"""
sprintkit.gps
=============

Provides GPS/Geographic classes and methods used internally by SprintKit.

:Copyright: (c) 2011 by Sprint.
:License: MIT, see LICENSE for more details.
"""

import collections
import math


class GeoDegree(int):
    """Data class representing a geographic coordinate degree componenent."""
    __slots__ = []
    
    def __new__(cls, value=None):
        if value is None:
            return int.__new__(cls, 0)
        if isinstance(value, int):
            if (value <= 90 and value >= -90) or (value <= 180 and value >= -180):

                return int.__new__(cls, value)
            raise ValueError("Value must be in the range: -180,180 or -90,90")
        raise ValueError("Value must be an int or a GeoDegree")

    def __neg__(self):
        return GeoDegree(-1*self)

    def __repr__(self):
        return "%i" % self

    def __str__(self):
        return u"%i\xb0".encode('utf-8') % self


class GeoMinute(int):
    """Data class representing a geographic coordinate minute componenent."""
    __slots__ = []
    
    def __new__(cls, value=None):
        if value is None:
            return int.__new__(cls, 0)
        if isinstance(value, int):
            if value <= 60 and value >= 0:
                return int.__new__(cls, value)
            raise ValueError("Value must be in the range: 0 to 60")
        raise ValueError("Value must be an int or a GeoMinute")

    def __repr__(self):
        return "%i" % self

    def __str__(self):
        return "%i'" % self

    def __neg__(self):
        raise ValueError("Value cannot be negative")


class GeoSecond(float):
    """Data class representing a geographic coordinate second componenent."""
    __slots__ = []
    
    def __new__(cls, value=None):
        if value is None:
            return float.__new__(cls, 0.0)
        if isinstance(value, float):
            if value <= 60.0 and value >= 0.0:
                return float.__new__(cls, value)
            raise ValueError("Value must be in the range: 0.0 to 60.0")
        raise ValueError("Value must be a float or a GeoSecond")
    
    def __neg__(self):
        raise ValueError("Value cannot be negative")

    def __repr__(self):
        return "%.2f" % self

    def __str__(self):
        return "%.2f\"" % self


class Latitude(float):
    """ Latitude value """

    __slots__ = []

    def __new__(cls, value=None):
        if value is None:
            return float.__new__(cls, 0.0)
        if isinstance(value, float):
            if value <= 90.0 and value >= -90.0:
                return float.__new__(cls, value)
            raise ValueError("Value must be in the range: -90.0 to 90.0")
        raise ValueError("Value must be a float or a Latitude")

    def __repr__(self):
        return "%2.6f" % self

    def __str__(self):
        (degree, minute, second) = self.dms()
        result = u"%i\xb0 %i' %.2f\"".encode('utf-8') % (abs(degree), minute, second)
        if self < 0: 
            return result + ' S'
        else: 
            return result + ' N'

    def __neg__(self):
        return Latitude(-1*self)

    @staticmethod
    def fromdms(degree, minute, second, direction=None):
        """Create a Latitude object from deg, min, sec values (and direction)
        
        :Parameters:
            * degree (integer)
            * minute (integer)
            * second (integer)
            * direction (string) - One of the following ['N','S']

        :Returns: Latitude

        """
        if direction is not None and direction not in ['N','S']:
            raise ValueError("The direction must be either 'N' or 'S'")
        if direction == 'S' and degree < 0:
            raise ValueError("Degree can't be negative if direction is S")
        if degree < 0:
            direction = 'S'
        degree = abs(int(degree))
        minute = int(minute)
        second = float(second)
        degdec = degree + (minute * 60.0 + second)/3600.0
        if direction == 'S':
            degdec = -degdec
        return Latitude(degdec)
    
    def dms(self):
        """Convert a floating point Latitude to degrees, minutes, seconds
        
        Returns:    namedtuple -- 
                    DMS(degrees=GeoDegree,minutes=GeoMinute,seconds=GeoSecond)
        """
        lat = self
        negative = lat < 0
        lat = abs(lat)
        degrees = GeoDegree(int(math.floor(lat)))
        lat = (lat - degrees) * 60
        minutes = GeoMinute(int(math.floor(lat)))
        seconds = GeoSecond((lat - minutes) * 60)
        if negative: 
            degrees = -degrees
        dms = collections.namedtuple('DMS','degrees minutes seconds')
        return dms(degrees, minutes, seconds)

    @property
    def degrees(self):
        """The decimal degrees of this Latitude object as a GeoDegree"""
        lat = self
        negative = lat < 0
        lat = abs(lat)
        degrees = GeoDegree(int(math.floor(lat)))
        if negative: 
            degrees = -degrees
        return degrees

    @property
    def minutes(self):
        """The decimal minutes of this Latitude object as a GeoMinute"""
        lat = self
        lat = abs(lat)
        degrees = GeoDegree(int(math.floor(lat)))
        lat = (lat - degrees) * 60
        return GeoMinute(int(math.floor(lat)))
    
    @property
    def seconds(self):
        """The decimal seconds of this Latitude object as a GeoSecond"""
        lat = self
        lat = abs(lat)
        degrees = GeoDegree(int(math.floor(lat)))
        lat = (lat - degrees) * 60
        minutes = GeoMinute(int(math.floor(lat)))
        return GeoSecond((lat - minutes) * 60)


class Longitude(float):
    """A class representing a floating point longitude"""

    __slots__ = []

    def __new__(cls, value=None):
        if value is None:
            return float.__new__(cls, 0.0)
        if isinstance(value, float):
            if value <= 180.0 and value >= -180.0:
                return float.__new__(cls, value)
            raise ValueError("Value must be in the range: -180.0 to 180.0")
        raise ValueError("Value must be a float or a Latitude")

    def __repr__(self):
        return "%2.6f" % self

    def __str__(self):
        (degree, minute, second) = self.dms()
        result = u"%i\xb0 %i' %.2f\"".encode('utf-8') % (abs(degree), minute, second)
        if self < 0: 
            return result + ' W'
        else: 
            return result + ' E'

    def __neg__(self):
        return Longitude(-1*self)

    @staticmethod
    def fromdms(degree, minute, second, direction=None):
        """Create a Longitude object from deg, min, sec values (and direction)
        
        Arguments:
            degree - int
            minute - int
            second - float
            direction - string ('E','W)

        Returns - Longitude
        """
        if direction is not None and direction not in ['E','W']:
            raise ValueError("The direction must be either 'E' or 'W'")
        if direction == 'W' and degree < 0:
            raise ValueError("Degree can't be negative if direction is W")
        if degree < 0:
            direction = 'W'
        degree = abs(int(degree))
        minute = int(minute)
        second = float(second)
        degdec = degree + (minute * 60.0 + second)/3600.0
        if direction == 'W':
            degdec = -degdec
        return Longitude(degdec)

    def dms(self):
        """Convert a floating point Latitude to degrees, minutes, seconds
        
        Returns:    namedtuple -- 
                    DMS(degrees=GeoDegree,minutes=GeoMinute,seconds=GeoSecond)
        """
        lng = self
        negative = lng < 0
        lng = abs(lng)
        degrees = GeoDegree(int(math.floor(lng)))
        lng = (lng - degrees) * 60
        minutes = GeoMinute(int(math.floor(lng)))
        seconds = GeoSecond((lng - minutes) * 60)
        if negative: 
            degrees = -degrees
        dms = collections.namedtuple('DMS','degrees minutes seconds')
        return dms(degrees, minutes, seconds)
    
    @property
    def degrees(self):
        """The decimal degrees of this Longitude object as a GeoDegree"""
        lng = self
        negative = lng < 0
        lng = abs(lng)
        degrees = GeoDegree(int(math.floor(lng)))
        if negative: 
            degrees = -degrees
        return degrees

    @property
    def minutes(self):
        """The decimal minutes of this Longitude object as a GeoMinute"""
        lng = self
        lng = abs(lng)
        degrees = GeoDegree(int(math.floor(lng)))
        lng = (lng - degrees) * 60
        return GeoMinute(int(math.floor(lng)))

    @property
    def seconds(self):
        """The decimal seconds of this Longitude object as a GeoSecond"""
        lng = self
        lng = abs(lng)
        degrees = GeoDegree(int(math.floor(lng)))
        lng = (lng - degrees) * 60
        minutes = GeoMinute(int(math.floor(lng)))
        return GeoSecond((lng - minutes) * 60)


class Coordinates(tuple):
    """A geographic coordinate stored in Latitude and Longitude pairs"""


    def __init__(self, latlong):
        if isinstance(latlong, tuple) and len(latlong) == 2:
            (latitude, longitude) = latlong
            self = (Latitude(latitude), Longitude(longitude))
        elif isinstance(latlong, Coordinates):
            self = (Latitude(latlong.latitude), Longitude(latlong.longitude))
        else:
            raise ValueError("Value must be a (Latitude, Longitude) tuple or a Coordinates instance") 

    def __repr__(self):
        return "(%s, %s)" % (repr(self.latitude), repr(self.longitude))
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__): 
            raise TypeError("Instance must be of type Coordinates")
        return self.latitude == other.latitude and self.longitude == other.longitude

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "Latitude: %s\nLongitude: %s" % (str(self.latitude), 
                str(self.longitude))
    
    def __sub__(self, other):
        """Haversine formula for calculating distance from these coordinates
        to `other` coordinates.
        
        :Returns: (int) - The distance in meters."""
        lat1, lon1 = self
        lat2, lon2 = other
        radius = 6371009 #Earth mean radius as defined by IUGG
        dist_lat = math.radians(lat2-lat1)
        dist_lon = math.radians(lon2-lon1)
        a = math.sin(dist_lat/2) * math.sin(dist_lat/2) +\
                math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *\
                math.sin(dist_lon/2) * math.sin(dist_lon/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = radius * c
        return int(distance)
   
    @property
    def latitude(self):
        """The latitude of this coordinate as a Latitude object"""
        return Latitude(self[0])

    @property
    def longitude(self):
        """The longitude of this coordinate as a Longitude object"""
        return Longitude(self[1])



class GpsFix(object):
    """A Class representing GPS Fix data (latitude, longitude, etc.)."""


    def __init__(self, timestamp, coordinates):
        self.timestamp = timestamp
        self.coordinates = coordinates

    def __str__(self):
        return "Time: %s\n%s" % (self.timestamp, str(self.coordinates))



class Gps2dFix(GpsFix):
    """A Class representing GPS Fix data (latitude, longitude, etc.).
    
    :Attributes:
        * timestamp (datetime)  - datetime object
        * coordinates (Coordinates) - The coordinates of the fix
        * heading (integer) - The heading 
        * speed (integer) - The speed
        * errors (dict) - Any errors that may have occurred (key/vals)
    
    """

    def __init__(self, timestamp, coordinates, heading=None, speed=None, 
                 errors=None):
        self.heading = heading
        self.speed = speed
        self.errors = errors
        GpsFix.__init__(self, timestamp, coordinates)

    def __str__(self):
        txt = "Time: %s\n%s\n" % (self.timestamp, self.coordinates)
        if self.heading is not None and self.speed is not None:
            txt += "Heading: %s\nSpeed: %s\n" % (self.heading, self.speed)
        elif self.errors is not None:
            if 'hepe' in self.errors:
                txt += "Horizontal Estimated Position Error (HEPE): %i meters\n" % self.errors['hepe']
        return txt

    
class Gps3dFix(GpsFix):
    """A Class representing GPS Fix data (latitude, longitude, etc.)."""


    def __init__(self, timestamp, coordinates, altitude=None, heading=None,
            speed=None, climb=None):
        self.timestamp = timestamp
        self.coordinates = coordinates
        self.altitude = altitude
        self.heading = heading
        self.speed = speed
        self.climb = climb

    def __str__(self):
        return "Time: %s\n%s" % (self.timestamp, str(self.coordinates))

class Satellite(object):
    """Class representing a GPS Satellite being used for a fix.
    
    :Attributes:
        * prn (integer) - Satellite PRN Number used to identify satellite, 
            the same as the Satellite Vehicle ID (SVID). 
        * elavation (integer) - Satellite elevation. (0-90)
        * azimuth (intger) - Satellite azimuth. degrees (0-360)
        * snr (integer) - Satellite Signal to Noise Ration. db (0-99)
        * used (bool) - Whether a satellite is used in the latest fix.

    """

    def __init__(self, prn, elv, azi, snr, used):
        self.prn = prn #: Satellite PRN Number same as Sat Vehicle ID (1-32)
        self.elevation = elv    #: Satellite elevation in degrees (0-90)
        self.azimuth = azi      #: Satellite azimuth in degrees (0-360)
        self.snr = snr          #: Satellite Signal to Noise Ratio in db (0-99)
        self.used = used
    
    def __repr__(self):
        return "Satellite PRN: %3d  Elv: %3d  Azi: %3d  SNR: %3d  Used: %s" % (
            self.prn, self.elevation, self.azimuth, self.snr, self.used)


SPRINTHQ = Coordinates((38.914812,-94.657734))
CLBROWN = Coordinates((38.922658,-97.213898))
