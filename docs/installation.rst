============
Installation
============


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
the Internet using either `pip` or Setuptools `easy_install`. I prefer Pip
because it handles dependencies and provides an unistall mechanism.

Pip (the easy way)
----------------------
Installing SprintKit using pip is the easiest way to get up and going quickly,
but first you need make sure you have a recent version of 
`distribute` installed::

    $ curl -O http://python-distribute.org/distribute_setup.py
    $ sudo python distribute_setup.py
    $ easy_install pip

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



