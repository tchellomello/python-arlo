Python Arlo
-----------

.. image:: https://badge.fury.io/py/pyarlo.svg
    :target: https://badge.fury.io/py/pyarlo

.. image:: https://travis-ci.org/tchellomello/python-arlo.svg?branch=master
    :target: https://travis-ci.org/tchellomello/python-arlo

.. image:: https://coveralls.io/repos/github/tchellomello/python-arlo/badge.svg
    :target: https://coveralls.io/github/tchellomello/python-arlo

.. image:: https://img.shields.io/pypi/pyversions/pyarlo.svg
    :target: https://pypi.python.org/pypi/pyarlo


Python Arlo  is a library written in Python 2.7/3x that exposes the Netgear Arlo cameras as Python objects.

Installation
------------

.. code-block:: bash

    $ pip install pyarlo

    # Install latest development
    $ pip install \
        git+https://github.com/tchellomello/python-arlo@dev

Usage
-----

.. code-block:: python

    # list devices
    from pyarlo import PyArlo
    arlo  = PyArlo('foo@bar', 'secret')

    arlo.devices
    {'cameras': [<ArloCamera: Garage>,  <ArloCamera: Patio>,
      <ArloCamera: Front Door>, <ArloCamera: Patio Gate>]}

    # list all cameras
    arlo.cameras
    [<ArloCamera: Garage>, <ArloCamera: Patio>,
     <ArloCamera: Front Door>, <ArloCamera: Patio Gate>]

    # by default, all videos recorded within
    # the last 30 days will be pre-loaded
    arlo.ArloMediaLibrary
    <ArloMediaLibrary: 235-1496386>

    arlo.ArloMediaLibrary.videos
    [<ArloVideo: Garage_1493171207448: 00:01:00>,
     <ArloVideo: Garage_1493171017009: 00:01:00>,
     <ArloVideo: Garage_1493160064553: 00:01:00>,
     <ArloVideo: Garage_1493159912748: 00:01:00>,
     <ArloVideo: Garage_1493159122023: 00:01:00>,
     <ArloVideo: Garage_1493153854245: 00:01:00>,
     <ArloVideo: Garage_1493120234227: 00:01:00>,
     <ArloVideo: Garage_1492565105936: 00:01:00>,
     <ArloVideo: Garage_1492565031836: 00:01:00>]


    # showing a video properties
    vdo = arlo.ArloMediaLibrary.videos[0]
    vdo.camera
    <ArloCamera: Garage>

    # downloading video
    vdo.download_video('/home/user/garage.mp4')
    True
