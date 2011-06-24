This chapter contains the API documentation. Much of this reference material
has been created automatically from docstrings in the code. Use the API
reference to understand in more detail how the methods and classes work. This
chapter parallels the modules in the package.

sprintkit.services
==================

The services module provides a set of convenience classes to make it a snap to
connect to and use services within Sprint's Developer Sandbox. These classes are
really just a thin wrapper around the Sandboxes' REST API.

The Sandbox services can be grouped into four basic functions which will be
described in more detail later;

    * Device Management
    * Messaging
    * Presence
    * Location Based Services

.. module:: sprintkit.services

Sandbox Configuration
---------------------

.. autoclass:: Config
    :members:

Device Management
-----------------

.. autoclass:: Account
    :members:


Messaging
---------

SMS
^^^

.. autoclass:: SMS
    :members:

Presence
--------

.. autoclass:: Presence
    :members:

Location Based Services
-----------------------

.. autoclass:: Location
    :members:

.. autoclass:: GeoFence
    :members:

.. autoclass:: Perimeter
    :members:


sprintkit.gps
=============

.. module:: sprintkit.gps

.. autoclass:: Coordinates
    :members:

.. autoclass:: Gps2dFix
    :members:


sprintkit.errors
================

.. module:: sprintkit.errors

.. autoclass:: SprintkitError
    :members:

.. autoclass:: ParsingError
    :members:

.. autoclass:: SandboxError
    :members:
