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

Developer Documentation: `http://python-arlo.readthedocs.io/ <http://python-arlo.readthedocs.io/>`_


Installation
------------

.. code-block:: bash

    $ pip install pyarlo

    # Install latest development
    $ pip install git+https://github.com/tchellomello/python-arlo@dev

Usage
-----

.. code-block:: python

    # connecting
    from pyarlo import PyArlo
    arlo  = PyArlo('foo@bar', 'secret')

    # listing devices
    arlo.devices

    # listing base stations
    arlo.base_stations

    # get base station handle
    # assuming only 1 base station is available
    base = arlo.base_stations[0]

    # listing Arlo modes
    base.available_modes
    ['armed', 'disarmed', 'schedule', 'custom']

    # listing all cameras
    arlo.cameras

    # showing camera preferences
    cam = arlo.cameras[0]

    # check if camera is connected to base station
    cam.is_camera_connected
    True

    # setting a mode
    cam.mode = 'armed'

    # getting the current active mode
    cam.mode
    'armed'

    # printing camera attributes
    cam.serial_number
    cam.model_id
    cam.unseen_videos

    # get brightness value of camera
    cam.get_brightness

    # get signal strength of camera with base station
    cam.get_signal_strength
    
    # get flip property from camera
    cam.get_flip_state

    # get mirror property from camera
    cam.get_mirror_state

    # get power save mode value from camera
    cam.get_powersave_mode

    # get current battery level of camera
    cam.get_battery_level
    92

    # get boolean result if motion detection
    # is enabled or not
    cam.is_motion_detection_enabled
    True

    # get battery levels of all cameras
    # prints serial number and battery level of each camera
    base.get_camera_battery_level
    {'4N71235T12345': 92, '4N71235T12345': 90}    

    # get base station properties
    base.get_basestation_properties

    # get camera properties
    base.get_camera_properties

    # get camera rules
    base.get_camera_rules

    # get camera schedule
    base.get_camera_schedule

    # get camera motion detection sensitivity
    cam.get_motion_detection_sensitivity

    # refreshing camera properties
    cam.update()

    # gathering live_streaming URL
    cam.live_streaming()
    rtmps://vzwow72-z2-prod.vz.netgear.com:80/vzmodulelive?egressToken=b723a7bb_abbXX&userAgent=web&cameraId=48AAAAA

    # gather last recorded video URL
    cam.last_video.video_url

Loading Videos
--------------

.. code-block:: python

    # by default, all videos recorded within
    # the last 30 days will be pre-loaded
    arlo.ArloMediaLibrary.videos

    # Or you can load Arlo videos directly
    from pyarlo.media import ArloMediaLibrary
    library = ArloMediaLibrary(arlo, days=2)
    len(library.videos)

    # showing a video properties
    media = library.videos[0]

    # printing video attributes
    media.camera
    media.content_type
    media.media_duration_seconds

    # displaying thumbnail to stdout
    media.download_thumbnail()

    # downloading video
    media.download_video('/home/user/demo.mp4')


Contributing
------------

See more at CONTRIBUTING.rst
