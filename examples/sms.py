#!/usr/bin/env python
import sys
import getopt

from sprintkit import SMS
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
                print "Send a text message to a mobile phone.\n"
                print 'Usage: sms.py <mdn> "message"'
                return 1
        if len(args) != 2:
            raise Usage("You must specify an MDN and a message.")
        (mdn, msg) = args
        sms = SMS()
        sms.send(mdn, msg)
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
