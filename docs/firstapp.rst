======================
Writing Your First App
======================

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


