Sprint's Network APIs in Python
===============================

SprintKit (based upon the excellent `restkit` HTTP client) allows developers to
add mobile functionality to their Python apps by providing easy access to the
Sprint Developer Sandbox. The Sprint Developer Sandbox is a REST based gateway
to Sprint's network services including; Location, SMS, MMS, Presence, and
Geo-Fences.

Basic access to the Developer Sandbox is FR$$, so get signed-up and let's see
what you can build!

Python Dependencies
===================

SprinKit only has two required dependencies, the rest are only really needed if
you intend to hack on the source.

Required
--------
    * restkit - An HTTP Client used for managing HTTP connections.
    * http-parser - An HTTP Parser required by restkit.

Optional
--------
    * nose - Used for unit test discovery and automation.
    * sphinx - Used for creating the documenation. 

Installation
============

SprintKit can be found on the Python Package Index (PyPI) and installed over
the Internet using either `pip` or Setuptool's `easy_install`. I prefer Pip
because it handles dependencies and provides an unistall mechanism. 

The installation process has only been tested on Linux and Mac OSX. Since
http-parser is a C exstension module you need a gcc compiler and the Python
headers to build and install it. This isn't as scary as it seems and works out
of the box on Mac, but you might have to install a few more things on your
Linux machine. For instance if you are using a Debian based distro you will
need the python-dev package as well as build-essential. 

You might be able to get this all working under Windows (cygwin would probably
be the easiest), but I haven't tried it.

Pip (the easy way)
----------------------
Installing SprintKit using pip is the easiest way to get up and going quickly,
but first you need make sure you have a recent version of 
`distribute` installed::

    $ curl -O http://python-distribute.org/distribute_setup.py
    $ sudo python distribute_setup.py
    $ easy_install pip

Note: if you don't have curl installed you can use wget instead.

Once you have pip, the rest is easy. It will install all of SprintKit's run-time
dependencies for you::

    $ pip install sprintkit

I like to put everything in a Virtualenv to keep my dependency problems to a
minimum and make my Python environments repeatable. So, assuming you have
virtualenv installed, here is what the full install process looks like::

    $ pip install virtualenv
    $ virtualenv --no-site-packages --distribute sprintenv
    $ cd sprintenv
    $ source bin/activate
    $ pip install sprintkit


Configuration
=============

Before you use SprintKit for the first time, you need to create a configuration
file that contains your credentials for accessing the Sprint Developer Sandbox.
Of course its a good idea to get your credentials before writing the config
file.

Obtaining Sandbox Credentials
-----------------------------

Sprint provides access to the Developer Sandbox services for free, but you must
register to get your API key/secret. 

#. First `register <http://developer.sprint.com/ssl/load/registerUser.do>`_ with the `Sprint Developer Site <http://developer.sprint.com>`_ 
#. Next, `sign up <http://developer.sprint.com/site/global/services/use_sprint/register/p_register.jsp>`_ for Sandbox Services.
#. Finally, note `your Sandbox key and secret <https://developer.sprint.com/site/global/services/use_sprint/sandbox_key/p_sandbox_key.jsp>`_ for configuring SprintKit.

The free version of the Sandbox is intended for development and demo purposes
therefore it is limited to 500 requests per day. If you need unlimited access
you can `upgrade <https://developer-store.sprint.com/>`_ your account by
purchasing credits for the production version.

Write a Basic Configuration
---------------------------

The configuration file must be in standard `INI` format and include a
`[sprintkit]` section that stores the pertinent Sandbox configuration data.
Here is a basic configuration sample with the required field/value pairs::

    [sprintkit]
    key = <insert_your_key_here>
    secret = <insert_your_secret_here>
    protocol = http
    host = www.sprintdevelopersandbox.com
    port = 80
    path = /developerSandbox/resources/v1

SprintKit will automatically search for config files first in the current
working directory (sprintkit.conf) and then in the $HOME directory
(.sprintkit.conf). The easiest way to get up and running quickly is to save
your config file as `.sprintkit.conf` in your $HOME directory. If you want to
customize the configuration loading process or read config data from a
different file, read the documentation on the Config object for more details.

Quick Example (or two)
======================

SprintKit makes interfacing to the Sprint network a snap, here are a few
snippets that should give you an idea of what you can do.

Sometimes you just need to find out where a phone or device is located (think
lost phone). Here is a simple Geo-Location fix from the Python shell::

    >>> from sprintkit import Location
    >>> location = Location()
    >>> print location.locate("XXXXXXXXXX")

Lets say you want to send someone an SMS message as soon as they enter a
geo-graphic perimeter. Here is a sample to do
that::

    from time import sleep
    from sprintkit import Perimeter, SMS
    
    sms = SMS()
    starbucks = (38.912683, -94.660306)
    perimeter = Perimeter(starbucks, 2000)
    friends_phone = "XXXXXXXXXX"
    inside = perimeter.inside(friends_phone)
    while not inside:
        sleep(60)
        inside = perimeter.inside(friends_phone)
    sms.send(friends_phone, "Hey, can you bring me a latte?")


Help and Documentation
======================

SprintKit contains extensive Doc Strings, so the quickest way to learn it is to
use it from the Python shell::

    >>> from sprintkit import Perimeter
    >>> perimeter = Perimeter()
    >>> help(perimeter)

If you want to have a nicely formatted copy of the documentation you can
generate a pdf from the source::

    make docs
    open docs/_build/latex/sprintkit.pdf

.. [#] Only required for restkit versions 3.3 and higher.
