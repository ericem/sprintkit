"""
sprintkit.errors
================

Exceptions used in sprintkit.

:Copyright: (c) 2011 by Sprint.
:License: MIT, see LICENSE for more details.
"""

class SprintkitError(Exception):
    """Base Exception for errors raised by sprintkit apis"""


class ConnectionError(SprintkitError):
    """Exception raised when there was a problem opening a connection to the
    Sandbox."""


class ParsingError(SprintkitError):
    """This Exception gets thrown if SprintKit can't parse the JSON data
    returned by the Sandbox. This could be because the Sandbox has changed its
    API and is returning data in a format that is not expected by SprintKit in
    which case the SprintKit method that threw the exception needs
    updated. You should really never see this one, if so please report
    it as a bug."""
    def __init__(self, error, data):
        self.error = error
        self.data = data

    def __str__(self):
        return "Error parsing the Sandbox JSON data (%s). The Sandbox API may\
have changed, check the latest documentation.\n%s" % (self.error, self.data)


class SandboxError(SprintkitError):
    """Exception for errors returned by the Sandbox servers.
    
    :Paramters:
        * error (string) - The error string returned from Sandbox.
        * response (:class:`sprintkit.services.SandboxResponse`) - A Sandbox Response object.
    """

    def __init__(self, error):
        self.error_text = { 
            'INVALID_KEY': "Invalid Sandbox key.",
            'EXPIRED_KEY': "Expired Sandbox Key.",
            'MDN_NOTVALID': "You are not authorized to use this MDN.",
            'MDN_NOTOPTEDIN': "You are not authorized to use this MDN.",
            'INVALID_MDN': "This is not a valid 10 digit MDN.",
            'INVALID_SIGNATURE': "Invalid signature, perhaps your secret is wrong?",
            'FAILURE': "Generic Sandbox failure.",
            'ERROR': "Generic Sandbox error.",
            'EXHAUSTED_DIPS': "You have exhausted your Sandbox usage limits.",
            'SERVICE_TEMPORARILY_UNAVAILABLE': "Oops, that Sandbox service is \
down at the moment.",
            'RADIUS_LESS_THAN_MIN_RADIUS': "The requested radius is less than \
the minimum radius allowed, 2000m",
            'UNEXPECTED_ERROR': "The Sandbox encountered an unexpected error.",
            "DEVICE_NOT_FOUND": "Could not find the MDN."}
        self.error = error.upper()
        """The error returned from the sandbox."""
        self.msg = self.error_text.get(self.error, 
                                       "Unknown Sandbox Error: %s" % self.error)

    def __str__(self):
        return self.msg


class GeoFenceError(SandboxError):
    """"""
    def __init__(self, error):
        text = super(GeoFenceError, self).__init__(error)
        self.error_text.update({ 
            'UNKNOWN_RECIPIENT': "This recipient is not in the list of \
recipients associated with this fence.",
            'FENCE_NOTADDED': "Fence was not added by the Sandbox.",
            'DEVICE_NOTFOUND': "This GeoFence device does not exist.",
            'FENCE_NOTFOUND': "Could not find a fence with this Fence ID.",
            'INVALID_FENCE_ID': "This is not a valid Fence ID.",
            'FENCE_NOTACTIVATED': 'Could not activate this fence.',

            'DEVICE_NOTDELETED': "Error deleting this GeoFence device."})

