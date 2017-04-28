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

    # connecting
    from pyarlo import PyArlo
    arlo  = PyArlo('foo@bar', 'secret')

    # listing devices
    arlo.devices
    {'base_station': [<ArloBaseStation: Home>],
     'cameras': [<ArloCamera: Garage>,  <ArloCamera: Patio>,
      <ArloCamera: Front Door>, <ArloCamera: Patio Gate>]}

    # listing base stations
    arlo.base_stations
    [<ArloBaseStation: Home>]

    # listing all cameras
    arlo.cameras
    [<ArloCamera: Garage>, <ArloCamera: Patio>,
     <ArloCamera: Front Door>, <ArloCamera: Patio Gate>]

    # showing camera preferences
    garage_cam = arlo.cameras[3]
    garage_cam
    <ArloCamera: Garage>

    # printing camera attributes
    garage_cam.serial_number
    garage_cam.model_id

    # refreshing camera properties
    garage_cam.update()

    # setting camera mode
    garage_cam.mode = 'arm'

    # gathering live_streaming URL
    garage_cam.live_streaming()
    rtmps://vzwow72-z2-prod.vz.netgear.com:80/vzmodulelive?egressToken=b723a7bb_abbXX&userAgent=web&cameraId=48AAAAA

    # by default, all videos recorded within
    # the last 30 days will be pre-loaded
    arlo.ArloMediaLibrary
    <ArloMediaLibrary: 235-1496386>

    arlo.ArloMediaLibrary.videos
    [<ArloVideo: Garage_1493262125792: 00:01:00>,
     <ArloVideo: Garage_1493252480334: 00:01:00>,
     <ArloVideo: Front Door_1493250408464: 00:00:55>,
     <ArloVideo: Garage_1493250374496: 00:01:00>,
     <ArloVideo: Front Door_1493250162591: 00:01:00>,
     <ArloVideo: Garage_1493224918537: 00:00:35>,
     <ArloVideo: Garage_1493224835637: 00:01:00>,
     <ArloVideo: Garage_1493223888822: 00:01:00>,
     <ArloVideo: Garage_1493153854245: 00:01:00>,
     <ArloVideo: Garage_1493120234227: 00:01:00>,
     <ArloVideo: Garage_1492565105936: 00:01:00>,
     <ArloVideo: Garage_1492565031836: 00:01:00>]

    # showing a video properties
    media = arlo.ArloMediaLibrary.videos[0]
    media.camera
    <ArloCamera: Garage>

    # media content type
    media.content_type
    'video/mp4'

    # media lenght in seconds
    media.media_duration_seconds
    60

    # displaying thumbnail to stdout
    media.download_thumbnail()

    # downloading video
    media.download_video('/home/user/garage.mp4')
    True
