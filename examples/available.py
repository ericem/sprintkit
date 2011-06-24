#!/usr/bin/env python
"""This is a simple command line tool for checking the reachability
of a device. If a device is reachable, it is connected to the network
and can receive calls/messages."""
import sys
import getopt

from sprintkit import Presence
from sprintkit.errors import SandboxError



class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            options, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
            raise Usage(msg)
        for option, value in options:
            if option in ("-h", "--help"):
                print "Determine if a mobile phone is connected to the network.\n"
                print "Usage: available.py <mdn>"
                return 1
            else:
                print "Bad option"
        if len(args) != 1:
            raise Usage("You must specify at least one MDN")
        mdn = args[0]
        presence = Presence()
        if presence.reachable(mdn):
            print "The device %s is reachable." % mdn
        else:
            print "The device %s is not connected to the network, maybe it is turned off." % mdn
        return 1

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "For help use --help."
        return 2
    except SandboxError, err:
        print err
        return 2


if __name__ == "__main__":

    sys.exit(main())
