"""
sprintkit.services
==================

Implementations of most Developer Sandbox Services.

:Copyright: (c) 2011 by Sprint.
:License: MIT, see LICENSE for more details.
"""

from ConfigParser import SafeConfigParser
from datetime import datetime
from hashlib import md5
import json
import os
import time
import urlparse
import uuid

from restkit import Resource
from restkit.errors import RequestError, RequestTimeout, ResourceError

from sprintkit import errors
from sprintkit.gps import Coordinates, Gps2dFix


class Config(dict):
    '''Reads configuration information for the Sandbox API gateway.

    :Parameters:
        * path (string) - The path to your config file (default=None).


    :class:`Config` is a sub-classed version of dict and therefore can be used
    just like a dict to store Sandbox configuration information.  If you do not
    specify a `path` it will first try to read a config first from the current
    working directory from a file named `sprintkit.conf`, next it will try
    to read from the default path: `$HOME/.sprintkit.conf`
    
    The default config file is in ini format
    Here is a sample config file::

        [sprintkit]
            key = <sprint_developer_key>
            secret = <sprint_developer_secret>
            host = test.sprintdevelopersandbox.com
            path = /developerSandbox/resources/v1

    :class:`Config` will also try to read the Sandbox Key and Sandbox
    Secret from the environment variables `SPRINTKEY` and
    `SPRINTSECRET`. It will try these last so they can be used to
    override values stored in the configuration file.

    :class:`Config` does not provide file writing capabilities, so any
    changes made to a config instance programatically will need to be
    also made in the config file in order to make the changes permanent. 

    '''

    def __init__(self, path=None):
        if path == None:
            home_dir = os.path.expanduser('~')
            run_dir = os.getcwd()
            default_runpath = os.path.join(run_dir, "sprintkit.conf")
            default_homepath = os.path.join(home_dir, ".sprintkit.conf")
            if os.path.exists(default_runpath):
                self.path = default_runpath
            else:
                self.path = default_homepath
        else:
            self.path = path

    def load(self):
        """Read the configuration file from path stored in `self.path`.
        
        :Raises: (:class:`sprintkit.errors.SprintKitError`) - If config
            file could not be found.
        
        """
        if os.path.exists(self.path):
            config = {}
            config_file = open(self.path, 'r')
            parser = SafeConfigParser()
            parser.readfp(config_file)
            config.update(parser.items('sprintkit'))
            if os.environ.has_key('SPRINTKEY') and os.environ.has_key('SPRINTSECRET'):
                config['key'] = os.environ['SPRINTKEY']
                config['secret'] = os.environ['SPRINTSECRET']
            self.update(config)
        else:
            raise errors.SprintkitError('Could not find configuration file: %s' % self.path)
        return self


class SandboxResource(Resource):
    """A class that manages connections to Sandbox Resources.
    
    Sub-class this to add support for new Sandbox resources not yet available in
    SprintKit.

    SandboxResource is a sub-class of a restkit Resource, so it accepts all its
    parameters.
    
    """
    
    def __init__(self, config=None, **kwargs):
        if config is None:
            self.config = Config()
            """A :class:`Config` instance for storing Sandbox credentials."""
            self.config.load()
        else:
            self.config = config
        self.api_url = urlparse.urlunparse((self.config['protocol'], 
                                            self.config['host'], 
                                            self.config['path'], '', '', '')) 
        super(SandboxResource, self).__init__(self.api_url, 
                                              follow_redirect=True,
                                              max_follow_redirect=10, **kwargs)

    def parse_response(self, response):
        """Parse a restkit Response payload into a json data dict.
       
        :Parameters: response (:class:`restkit.wrappers.Response`) - Response

        :Returns: (dict) - The raw Sandbox JSON data.

        :Raises: :class:`sprintkit.errors.ParsingError`

        """
        try:
            body = response.body_string()
            data = json.loads(body)
        except:
            raise errors.ParsingError("Malformed JSON data", body)
        return data

    def parse_errors(self, data):
        """Parse raw Sandbox JSON data looking for Sandbox thrown errors.
        
        :Parameters: data (dict) - The raw Sandbox JSON data.

        :Raises: :class:`sprintkit.errors.SandboxError`
        """
        if 'error' in data.keys():
            raise errors.SandboxError(data['error'])


    def sign_params(self, params, secret):
        """Build a dict of URL parameters and add a sig
    
        :Parameters:
            * params (dict) - Dictionary of URL query param key/val pairs
            * secret (str) - The API Secret used to create signature.

        :Returns: (dict) - The parameters with a signature added.

        .. note::
            Read the documentation; http://goo.gl/Wu7T5 for details on
            generating the signature. Note, these parameters MUST NOT be
            url quoted, before generating the signature.
        
        """
        #Update the timestamp if there is one
        if 'timestamp' in params.keys():
            params['timestamp'] = self.make_timestamp()
        
        #Stringify all values
        for key, val in params.items():
            params[key] = str(val)

        #Update the authentication signature if there is one
        if 'sig' in params.keys():
            del(params['sig'])
            #Make the authentication signature slug
            pairs = ["%s%s" % (key, params[key]) for key in sorted(params.keys())]

            #Sign it using our secret
            rawsig = "".join(pairs) + secret
            params['sig'] = md5(rawsig).hexdigest()
        return params

    def make_timestamp(self):
        """Generate an API timestamp. 
        
        :Returns: (string) - The timestamp.

        .. note:: 
            The sandbox REST APIs require a timestamp parameter to help
            prevent replay attacks. This is a convienence utilty to
            create those timestamps so that they are properly formatted.

            The timestamp should be the current time in the format: 
            
            [YYYY]-[MM]-[DD]T[HH]:[MM]:[SS][ZZZ] 
            
            [HH] refers to a zero-padded hour between 00 and 23 (where
            00 is used to notate midnight at the start of a calendar
            day).

            
        """
        tnow = datetime.utcnow().replace(microsecond=0) #remove microseconds
        tzone = "UTC"
        timestamp = datetime.isoformat(tnow) + tzone
        return timestamp


class SMS(SandboxResource):
    """A Resource used to send SMS messages."""

    def send(self, mdns, msg):
        """Sends an SMS text message to a device or list of devices.
        
        :Parameters:
            * mdns (string) - The MDN(s) to send the message to. 
            * msg (string) - The text message (160 characters).
        
        .. note:: 
            The `mdns` parameter must be a valid 10-digit MDN, or a comma
            separated list of mdns. For example::

                mdns = "0005551111"
                mdns = "0005551111,0005551212"

        :Returns: (dict) - The raw JSON Sandbox data.
       
        .. note:: 
            Here is a sample response for a successful transaction::
                {'MessagingResponse': 
                    [{'status': 'S', 
                      'tranno': 'e6d6bd9', 
                      'mdn': '9995551212', 
                      'gcode': '1000'}]}
        
        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`


        """
        params = {'mdns': mdns, 
                  'msg': msg, 
                  'timestamp': True,
                  'key': self.config['key'], 
                  'sig': True}
        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('sms.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)
        #We only report the first error we find
        errs = [k for k in data.keys() if k != 'MessagingResponse']
        if errs:
            raise errors.SandboxError(errs[0])
        if not 'MessagingResponse' in data.keys():
            raise errors.ParsingError("Missing a MessagingResponse",
                response)
        return data


class Presence(SandboxResource):
    """A Resource to check if an MDN is reachable on the network.
    
    :Parameters: config (:class:`Config`) - The Sandbox configuration.
    """

    def get_presence(self, mdn):
        """Get the presence status of an MDN.
        
        :Parameters: mdn (string) - The MDN to check for reachability.

        :Returns: (dict) - The raw Sandbox JSON data.
        
        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`
        
        """
        params = {'mdn': mdn, 
                  'timestamp': True, 
                  'key': self.config['key'], 
                  'sig': True}

        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('presence.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)

        return data

    def reachable(self, mdn):
        """Check if an MDN is reachable.
        
        :Parameters: mdn (string) - The MDN to check for reachability.

        :Returns: (bool) - True if the `mdn` is reachable.
        
        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.SandboxError`
            * :class:`sprintkit.errors.ParsingError`

        .. note:: 
            This is a convenience method. The same data can be extracted using
            the `get_presence()` method.
        """
        data = self.get_presence(mdn)
        try:
            status = data['status']
        except KeyError as e:
            raise errors.ParsingError("KeyError: '%s'." % status, data)
        if status != 'Reachable' and status != 'Unreachable':
            raise errors.ParsingError("ValueError: 'status' is incorrect.", 
                                      data)
        return (status == 'Reachable')


class Location(SandboxResource):
    """A Resource for getting a location fix for an MDN.
    
    :Parameters: config (:class:`Config`) - The Sandbox configuration.
    """

    def get_location(self, mdn):
        """Get the location data for an `mdn`.
        
        :Parameters: mdn (string) - The MDN to get location fix for (10 digits).

        :Returns: (dict) - The raw Sandbox location data in JSON format.

        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.SandboxError`
            * :class:`sprintkit.errors.ParsingError` 
        """
        params = {'mdn': mdn, 
                 'timestamp': True, 
                 'key': self.config['key'], 
                 'sig': True}

        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('location.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)

        return data

    def locate(self, mdn):
        """Get the location data for an `mdn` (a convenience method).

        :Parameters: mdn (string) - The MDN to get location fix for (10 digits).

        :Returns: (:class:`sprintkit.gps.Gps2dFix`) - The Gps2dFix object
        
        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.SandboxError`
            * :class:`sprintkit.errors.ParsingError` 

        .. note:: 
            This is a convenience method that returns an instance of
            :class:`sprintkit.gps.Gps2dFix` which contains all of the
            pertinent location information. To get the lat/lon use the
            coordinates attribute::

                lat = Gps2dFix.coordinates.lattitude
                lon = Gps2dFix.coordinates.longitude
                (lat, lon) = Gps2dFix.coordinates
        """
        data = self.get_location(mdn)

        try:
            lat = float(data['lat'])
            lon = float(data['lon'])
            accuracy = int(data['accuracy'])
        except KeyError as e:
            raise errors.ParsingError("Missing %s" % e, data)
        except ValueError as e:
            raise errors.ParsingError(e, data)

        coord = Coordinates((lat,lon))

        return Gps2dFix(datetime.now(), coord, errors={'hepe':accuracy})


class Perimeter(SandboxResource):
    """A class used for checking if an mdn is within a geographic area 
    specified by its Coordinates and a radius in meters.
    
    :Parameters:
        * coordinates (:class:`sprintkit.gps.Coordinates`, or tuple) - The
            center lat/lon of the perimeter.  
        * radius (integer) - Radius of the perimeter in meters.

    .. note::
        The typical usage for Perimeter would be to create a perimeter based on
        a set of center coordinates and radius, then call its methods to check
        if devices are within the perimeter.
    """
    def __init__(self, coordinates, radius, config=None, **kwargs):
        self.coordinates = Coordinates(coordinates)
        self.radius = radius
        super(Perimeter, self).__init__(config, **kwargs)

    def get_perimeter(self, mdn):
        """Check if an mdn is inside this Perimeter.
        
        :Parameters: mdn (string): The mdn of the device to check

        :Returns: (dict) - The raw Sandbox JSON data.

        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.SandboxError`
            * :class:`sprintkit.errors.ParsingError` 
        """
        lat = repr(self.coordinates.latitude)
        lon = repr(self.coordinates.longitude)
        rad = str(self.radius)
        params = {'mdn': mdn, 
                 'lat': lat, 
                 'long': lon, 
                 'rad': rad, 
                 'timestamp': True, 
                 'key': self.config['key'], 
                 'sig': True}
        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('geofence/checkPerimeter.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)
        return data
    
    def inside(self, mdn):
        """Returns True if the mdn is inside this Perimeter.

        :Parameters: mdn (string): The mdn of the device to check the perimeter for.

        :Returns: (bool) - True if mdn is inside the perimeter, False otherwise.
        
        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.SandboxError`
            * :class:`sprintkit.errors.ParsingError`

        .. note::
            This method provides a simple perimeter check, if you also
            need to get the coordinates of the device at the same time
            as you check the perimeter, use the `get_perimeter` method
            instead.
        
        """
        data = self.get_perimeter(mdn)

        try:
            status = data['CurrentLocation'] 
        except KeyError as e:
            raise errors.ParsingError("Missing the CurrentLocation field", data) 

        if status != 'INSIDE' and status != 'OUTSIDE': 
            raise errors.ParsingError("ValueError for CurrentLocation", data)

        return (status == 'INSIDE')

    def check(self, mdn):
        """Check if an MDN is inside this Perimeter (a convenience
        method).
        
        :Parameters: mdn (string): The mdn of the device to check the perimeter for.

        :Returns: (tuple) - (bool, :class:`sprintkit.gps.Gps2dFix`) 
        
        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.SandboxError`
            * :class:`sprintkit.errors.ParsingError`

        .. note:: 
            This convenience method returns a tuple (inside, fix). The
            boolean `inside` is True if the device is inside the fence
            and `fix` contains :class:`sprintkit.gps.Gps2dFix` which has
            all of the pertinent location information. To get the
            lat/lon use the coordinates attribute of Gps2dFix::

                lat = Gps2dFix.coordinates.lattitude
                lon = Gps2dFix.coordinates.longitude
                (lat, lon) = Gps2dFix.coordinates
        """
        data = self.get_perimeter(mdn)
        timestamp = datetime.now()

        try:
            lat = float(data['Latitude'])
            lon = float(data['Longitude'])
            accuracy = float(data['Accuracy'])
            status = data['CurrentLocation'] 
        except KeyError as e:
            raise errors.ParsingError("Missing %s" % e, data)
        except ValueError as e:
            raise errors.ParsingError(e, data)

        coord = Coordinates((lat,lon))
        fix = Gps2dFix(timestamp, coord, errors={'hepe':accuracy})
        try:
            status = data['CurrentLocation'] 
        except KeyError as e:
            raise errors.ParsingError("Missing the CurrentLocation field", data) 
        if status != 'INSIDE' and status != 'OUTSIDE': 
            raise errors.ParsingError("ValueError for CurrentLocation", data)
        inside = (status == 'INSIDE')

        return (inside, fix)

    def distance_to(self, mdn):
        """Calculate the distance from the Perimeter to the `mdn`.
        
        :Parameters: 
            * mdn (string) - The device MDN to calculate distance to.

        :Returns: (int) - The distance to the MDN in meters. 

        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`

        .. note::
            This method does not use the Sandbox functions to calculate
            the distance, instead the location is first determined using
            the `locate()` method, then the distance to these
            coordinates is calculated using the haversine formula.
        """
        current_location = self.locate(mdn).coordinates
        return self.coordinates - current_location


class Fence(SandboxResource):
    """A Sandbox Resource for modifying geofences.

    :Parameters:
        * config (:class:`Config`) - The Sandbox configuration.
        * fenceid (integer): A unique number for identifying the fence.
        * name (string): A text name for the fence.
        * coordinates (:class:`sprintkit.gps.Coordinates`): The coordinates for the center of the fence.
        * radius (integer): The radius of fence in meters.
        * days (string): The days of week to monitor fence [SMTWHFA].
        * start_time (string): The time when fence becomes active "HHMM".
        * end_time (string): The time with fence becomes inactive "HHMM".

    .. note::
        This object is not intended to be instantiated by the end user
        directly, instead it is returned when calling the GeoFence.fences()
        method.

    """
    def __init__(self, fenceid, name, coordinates, radius, days, start_time, 
                 end_time, status, config=None, **kwargs):
        self.fenceid = fenceid
        self.name = name
        self.coordinates = coordinates
        self.radius = radius
        self.days = days
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        super(Fence, self).__init__(config, **kwargs)

    def activate(self):
        """Activate this Fence.

        :Returns: (dict) - The raw Sandbox JSON data.

        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`

        """
        params = {'fenceId': self.fenceid,
                 'timestamp': True, 
                 'key': self.config['key'], 
                 'sig': True}

        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('geofence/activate.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)

        try:
            message = data['Message']
        except KeyError:
            raise errors.ParsingError("Missing a `Message` field.", data)

        if message == 'FENCE_ACTIVATED':
            self.status = 'active'
            return data
        else:
            raise errors.GeoFenceError(message)
    
    def deactivate(self):
        """De-activate this Fence.
        
        :Returns: (dict) - The raw Sandbox JSON data.

        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`

        """
        params = {'fenceId': self.fenceid,
                  'timestamp': True, 
                  'key': self.config['key'], 
                  'sig': True}

        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('geofence/deactivate.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)

        return data

    def get_devices(self):
        """Returns the devices associated with this fence.
        
        :Returns: (dict) - The raw Sandbox JSON data. 

        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`

        """
        params = {'fenceId': self.fenceid,
                  'timestamp': True, 
                  'key': self.config['key'], 
                  'sig': True}

        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('geofence/listDevices.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)

        return data

    def devices(self):
        """Returns the devices associated with this fence (a convenience
        method).
       
        :Returns: (dict) - The devices associated with a fence.
        
        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`

        .. note:: 
        
        This method returns a dictionary that maps an mdn (string) to a
        deviceid (integer) for each device that is being monitored within this
        geofence. For example::
            
            devices = {"1115551212": 102}
        
        """
        result = self.get_devices()
        device_list = result['Device']
        devices = {}
        for device in device_list:
            if device.has_key('Message'):
                return devices
            devices[device['MDN']] = int(device['DeviceID'])
        return devices


    def add_device(self, mdn):
        """Add a device to be monitored inside this Fence.
        
        :Parameters: mdn (string) - The mdn of the device to be monitored.
        
        :Returns: (dict) - The raw Sandbox JSON data.

        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`

        """
        params = {'fenceId': self.fenceid,
                  'mdn': mdn,
                  'timestamp': True, 
                  'key': self.config['key'], 
                  'sig': True}

        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('geofence/addDevice.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)

        try:
            message = data['Message']
        except KeyError:
            raise errors.ParsingError("Missing a `Message` field.")

        if message != 'DEVICE_ADDED':
            raise errors.GeoFenceError(message)
        else:
            return data
    
    def delete_device(self, mdn):
        """Delete a device associated with this Fence.

        :Parameters: mdn (string) - The mdn of the device to be removed from monitoring.
        
        :Returns: (dict) - The raw Sandbox JSON data.

        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`

        .. note:: 
            The Sandbox does not provide a method to remove a device from a
            fence using its mdn, so we have to first make a call to
            get_devices() to get the deviceid associated with the mdn.

        """
        devices = self.devices()

        try:
            deviceid = devices[mdn]
        except KeyError:
            raise errors.GeoFenceError("DEVICE_NOTFOUND")

        params = {'deviceId': deviceid,
                  'timestamp': True, 
                  'key': self.config['key'], 
                  'sig': True}

        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('geofence/deleteDevice.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)

        try:
            message = data['Message']
        except KeyError:
            raise errors.ParsingError("Missing a `Message` field.")

        if message != 'DEVICE_DELETED':
            raise errors.GeoFenceError(message)
        else:
            return data


    def get_recipients(self):
        """Get the recipients of notification of geofence events.

        :Returns: (dict) - The raw Sandbox JSON data.

        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`

        """
        params = {'fenceId': self.fenceid,
                  'timestamp': True, 
                  'key': self.config['key'], 
                  'sig': True}
        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('geofence/listRecipients.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)
        return data

    def recipients(self):
        """Get the recipients of notification of geofence events.

        This is a convenience method. This method returns a dictionary
        that maps a recipient mdnurl (string) to a recpientid (integer).
        The mdnurl is either an MDN or a URL that events for this
        geofence will be sent. Here is a sample:: 

            recipients = {"1115551212": 105}

        :Returns: (dict)
        
        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`
        
        """
        result = self.get_recipients()
        recipients = {}
        recipient_list = result['Recipient']
        for recipient in recipient_list:
            try:
                recipients[recipient['MDNURL']] = int(recipient['RecipientID'])
            except:
                return recipients
        return recipients

    def add_recipient(self, recipient):
        """Add a recipient for a Fence notification event.
        
        :Parameters: recipient (string) - Either an MDN or a URL

        :Returns: (dict) - The raw Sandbox JSON data.
        
        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`

        """
        params = {'fenceId': self.fenceid,
                  'mdnURL': recipient,
                  'timestamp': True, 
                  'key': self.config['key'], 
                  'sig': True}
        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('geofence/addRecipient.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)
        return data

    def delete_recipient(self, recipient):
        """Delete a recipient of a geofence notification.
        
        :Parameters: recipient (string) - Either an MDN or a URL.
        
        :Returns: (dict) - The raw Sandbox JSON data.

        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`

        """
        recipients = self.recipients()
        if not recipients.has_key(recipient):
            raise errors.GeoFenceError("UNKNOWN_RECIPIENT")
        recipientid = recipients[recipient]
        params = {'recipientId': recipientid,
                  'timestamp': True, 
                  'key': self.config['key'], 
                  'sig': True}
        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('geofence/deleteRecipient.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)
        return data


class GeoFence(SandboxResource):
    """A SandboxResource to retrieve and create geofences.
    
    :Parameters: config (:class:`Config`) - The Sandbox configuration.
    
    """
   
    def get_fences(self):
        """Get all of the geofences associated with a Sandbox user account.
        
        :Returns: (dict) - The raw Sandbox JSON data.
        
        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`

        .. note::
            This method retrieves the list of geofences for this user account.  
            Here is a sample of the data returned::

                {u'Fence': [{u'Status': u'Inactive', 
                             u'FenceID': u'139', 
                             u'Name': u'test', 
                             u'Days': u'W', 
                             u'Longitude': 
                             u'-94.1234', 
                             u'StartTime': u'1100', 
                             u'Latitude': u'38.1234', 
                             u'LastMonitorTime': u'NEVER', 
                             u'EndTime': u'2200', 
                             u'Dimensions': u'2000'}]}

        """
        params = {'timestamp': True, 
                 'key': self.config['key'], 
                 'sig': True}
        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('geofence/list.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)
        return data

    def fences(self, match=None):
        """Get all of the geofences associated with a Sandbox user account.

        :Parameters:
            * match - (int or string) - The `fenceid` or `name` of a fence.

        :Returns: (list) - A List of Fence objects.
        
        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`
       
        .. note:: 
            This method returns a list of Fence objects. Each Fence
            represents a Sandbox geofence. With the Fence objects you
            can control the individual geofences. You can filter the
            list of Fence objects by supplying a `match` argument. This
            is either the name of the geofence (string) or the fenceid
            (an integer).
        
        """
        fences = []
        data = self.get_fences()
        try:
            for fence in data['Fence']:
                if 'Message' in fence.keys():
                    return []
                fenceid = int(fence['FenceID'])
                name = fence['Name']
                lat = float(fence['Latitude'])
                lon = float(fence['Longitude'])
                coordinates = Coordinates((lat,lon))
                radius = int(fence['Dimensions'])
                days = fence['Days']
                start_time = fence['StartTime']
                end_time = fence['EndTime']
                status = fence['Status'].lower()
                if match:
                    if isinstance(match, str) and match == name:
                        fences.append(Fence(fenceid, name, coordinates, radius, 
                                            days, start_time, end_time, status, 
                                            self.config))
                    elif isinstance(match, int) and match == fenceid:
                        fences.append(Fence(fenceid, name, coordinates, radius, 
                                            days, start_time, end_time, status, 
                                            self.config))
                    else:
                        continue
                else:
                    fences.append(Fence(fenceid, name, coordinates, radius, days, 
                                     start_time, end_time, status, self.config))


        except KeyError as e:
            raise errors.ParsingError("KeyError '%s'." % e, data)
        return fences


    def add_fence(self, name, start_time, end_time, coordinates, 
                  radius, interval, days, notify_event):
        """Add a fence to a Sandbox user account.
        
        :Parameters:
            * name (string) - A name to give this geofence.
            * start_name (string) - Time when the fence becomes active "HHMM"
            * end_time (string) - Time when the fence becomes inactive "HHMM"
            * coordinates (:class:`sprintkit.gps.Coordinates`) - The lat/lon
                center of the fence.
            * radius (integer) - Radius of fence in meters.
            * interval (integer) - How often to check the fence (in 5 minute increments).
            * days (string) - Days of week to check the fence.
            * notify_event (string) - What event triggers a notification.

        .. note::
            The `days` parameter is a string that corresponds to which days of the
            week that a fence will be active. Each day of the week is represented
            by a letter, and these letters can be concatenated::

                sunday = 'S'
                monday = 'M'
                tuesday = 'T'
                wednesday = 'W'
                thursday = 'H'
                friday = 'F'
                saturday = 'A'
                days = sunday + wednesday + friday
                days = "SWF" #Active on days Sunday, Wednesday and Friday

            The `start_time` and `end_time` parameters are strings that represent
            what time a fence will become active and what time it will become
            inactive. The string is in the format "HHMM"" where HH is the 24-hour
            time (00-23) where 00 is midnight. MM is the minutes (00-59). 

            The `notify_event` parameter specifies whether the fence should
            notify on 'in', 'out' or 'both' events.

        :Returns: (:class:`sprintkit.services.Fence`) - The Fence that was
            added.
        
        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`

        """
        coordinates = Coordinates(coordinates)
        params = {'name': name,
                  'strtTime': start_time,
                  'endTime': end_time,
                  'lat': repr(coordinates.latitude),
                  'long': repr(coordinates.longitude),
                  'dim': radius,
                  'interval': interval,
                  'days': days,
                  'notifyEvent': notify_event,
                  'timestamp': True,
                  'key': self.config['key'],
                  'sig': True}
        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('geofence/add.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)
        if data['message'] == 'FENCE_ADDED':
            fenceid = int(data['ID'])
            fence = [fence for fence in self.fences() if fence.fenceid == fenceid]
            if len(fence) == 1:
                return fence[0]
            else:
                raise errors.GeoFenceError("FENCE_NOTADDED")
        else:
            raise errors.GeoFenceError(data['message'])

    def delete_fence(self, fence):
        """Delete a geofence from this account.
        
        :Parameters: (:class:`sprintkit.services.Fence`) - A Fence object.

        :Returns: (dict) - The raw Sandbox JSON data.
        
        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`
        
        """
        params = {'fenceId': fence.fenceid,
                  'timestamp': True, 
                  'key': self.config['key'], 
                  'sig': True}
        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('geofence/delete.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)
        return data


class Account(SandboxResource):
    """A class for configuring devices associated with a developer account.

    :Parameters:
        * config (dict) - A :class:`Config` instance (default=None).

    """

    def get_devices(self, status=None, mdn=None):
        """Retrieve devices associated with this developer account.

        :Optional Parameters:
            * status (string) - The authorization status criteria to filter on.
            * mdn (string) - The MDN to get status for.

        :Returns: (dict) - The raw JSON Sandbox Data.

        .. note:: 
            Retrieves all of the devices associated with this developer
            account. The devices to be returned can be filtered by
            specifying either a device `status` or an `mdn`. 

            The `status` parameter filters the devices that are returned. It
            has the following permitted values: 

            'p' for devices that are `pending`, 
            'a' for devices that are `approved`, 
            'x' for devices that are `declined`, and 
            'd' for devices that have been `deleted`.

            The `mdn` parameter can be used to return authorization status for
            a single device instead of all devices associated with this
            account.
            
            The authorization data is returned as a dict. Here is an example:: 
                
                {"username": "your_username",
                 "devices": {
                      "approved": ["1115551212", "1115551213"],
                      "declined": [],
                      "pending": [],
                      "deleted": ["1115551234"]},
                  "authStatus": "Declined"}
        
        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`

        """
        params = {'key': self.config['key'],
                  'timestamp': True,
                  'sig': True}
        if status:
            params[status] = status
        if mdn:
            params[mdn] = mdn
        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('devices.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)
        return data
        
    def add_device(self, mdn):
        """Add a device to this developer account.
        
        :Parameters: mdn (string) - The MDN to add to this account.

        :Returns: (dict) - The raw JSON Sandbox data.
        
        .. note::
            This method returns a dict containing the status of the add
            operation. On success it returns the following::

                {u'response': u'SUCCESS'}

            If the Sandbox could not add the device to the account it
            returns a failure message, for example::

                {u'response': u'FAILED'}

        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`
        """
        params = {'method': 'add',
                  'mdn': mdn,
                  'key': self.config['key'],
                  'timestamp': True,
                  'sig': True}
        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('device.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)
        return data

    def delete_device(self, mdn):
        """Delete a device from this developer account.
        
        :Parameters: mdn (string) - The MDN to add to this account.

        :Returns: (dict) - The raw JSON sandbox data.
        
        .. note::
            On success returns::
                {u'response': u'SUCCESS'}

        :Raises: 
            * :class:`sprintkit.errors.ConnectionError`
            * :class:`sprintkit.errors.ParsingError`
            * :class:`sprintkit.errors.SandboxError`
       

        """
        params = {'method': 'delete',
                  'mdn': mdn,
                  'key': self.config['key'],
                  'timestamp': True,
                  'sig': True}
        params = self.sign_params(params, self.config['secret'])
        try:
            response = self.get('device.json', params_dict=params)
        except (RequestError, RequestTimeout) as e:
            raise errors.ConnectionError(str(e))
        data = self.parse_response(response)
        self.parse_errors(data)
        return data

