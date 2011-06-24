#!/usr/bin/env python
import sys
import getopt

from sprintkit import Location
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
                print "Locate a mobile phone by its MDN (mobile directory number)\n"
                print "Usage: locate.py <mdn>"
                return 1
        if len(args) != 1:
            raise Usage("You must specify at least one MDN")
        location = Location()
        print location.locate(args[0])
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "For help use --help."
        return 2
    except SandboxError, err:
        print err
        return 2


if __name__ == "__main__":

    sys.exit(main())
