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

    # listing Arlo modes
    base.available_modes
    ['armed', 'disarmed', 'schedule', 'custom']

    # setting a mode
    garage_cam.mode = 'armed'

    # listing all cameras
    arlo.cameras

    # showing camera preferences
    cam = arlo.cameras[0]

    # printing camera attributes
    cam.serial_number
    cam.model_id
    cam.unseen_videos

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
