Python Arlo
-----------

.. image:: https://badge.fury.io/py/pyarlo.svg
    :target: https://badge.fury.io/py/pyarlo

.. image:: https://travis-ci.org/tchellomello/python-arlo.svg?branch=master
    :target: https://travis-ci.org/tchellomello/python-arlo

.. image:: https://coveralls.io/repos/github/tchellomello/python-arlo/badge.svg?branch=master
    :target: https://coveralls.io/github/tchellomello/python-arlo?branch=master

.. image:: https://img.shields.io/pypi/pyversions/pyarlo.svg
    :target: https://pypi.python.org/pypi/pyarlo

.. _CONTRIBUTING.rst: https://raw.githubusercontent.com/tchellomello/python-arlo/master/CONTRIBUTING.rst

RETIRED:
--------
Please visit the awesome work by @twrecked at https://github.com/twrecked/hass-aarlo


Python Arlo  is a library written in Python 2.7/3x that exposes the Netgear Arlo cameras as Python objects.

Developer Documentation: `http://python-arlo.readthedocs.io/ <http://python-arlo.readthedocs.io/>`_


Installation
------------

.. code-block:: bash

    $ pip install pyarlo

    # Install latest development
    $ pip install git+https://github.com/tchellomello/python-arlo

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

    # get the current base station mode
    base.mode  # 'disarmed'

    # listing Arlo modes
    base.available_modes # ['armed', 'disarmed', 'schedule', 'custom']

    # Updating the base station mode
    base.mode = 'custom'

    # listing all cameras
    arlo.cameras

    # showing camera preferences
    cam = arlo.cameras[0]

    # check if camera is connected to base station
    cam.is_camera_connected  # True

    # printing camera attributes
    cam.serial_number
    cam.model_id
    cam.unseen_videos

    # get brightness value of camera
    cam.brightness

    # get signal strength of camera with base station
    cam.signal_strength
    
    # get flip property from camera
    cam.flip_state

    # get mirror property from camera
    cam.mirror_state

    # get power save mode value from camera
    cam.powersave_mode

    # get current battery level of camera
    cam.battery_level
    92

    # get boolean result if motion detection
    # is enabled or not
    base.is_motion_detection_enabled  # True

    # get battery levels of all cameras
    # prints serial number and battery level of each camera
    base.get_cameras_battery_level  # {'4N71235T12345': 92, '4N71235T12345': 90}

    # get base station properties
    base.properties

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
    cam.live_streaming()  # rtmps://vzwow72-z2-prod.vz.netgear.com:80/vzmodulelive?egressToken=b723a7bb_abbXX&userAgent=web&cameraId=48AAAAA

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


Ambient Sensors Data Usage (Arlo Baby Monitor)
----------------------------------------------

.. code-block:: python

    # Get the base_station instance corresponding to the Arlo Baby
    base_station = arlo.base_stations[0]

    # Store all ambient sensor history in self._ambient_sensor_data
    # All of the accessor properties will call this if values are not cached.
    base_station.get_ambient_sensor_data()

    # Get cached sensor history (property)
    base_station.ambient_sensor_data

    # Get most recent temperature reading in degrees celsius (property)
    base_station.ambient_temperature

    # Get most recent humidity reading in relative humidity percentage (property)
    base_station.ambient_humidity

    # Get most recent air quality reading (property)
    # Not 100% sure on the unit of measure, but would assume it's VOC PPM
    base_station.ambient_air_quality

Music Playback Usage (Arlo Baby Monitor)
----------------------------------------

.. code-block:: python

    # Get the current playback status and available track list
    base_station.get_audio_playback_status()

    # Play a track, optionally specify the track and seek time in seconds
    base_station.play_track(
        track_id='229dca67-7e3c-4a5f-8f43-90e1a9bffc38',
        position=0)

    # Pause the currently playing track
    base_station.pause_track()

    # Skip to the next track in the playlist
    base_station.skip_track()

    # Set the music loop mode to repeat the entire playlist
    base_station.set_music_loop_mode_continuous()

    # Set the music loop mode to repeat the current track
    base_station.set_music_loop_mode_single()

    # Sets playback to shuffle
    base_station.set_shuffle_on()

    # Sets playback to sequential
    base_station.set_shuffle_off()

    # Change the playback volume
    base_station.set_volume(100)

Night Light Usage (Arlo Baby Monitor)
-------------------------------------

.. code-block:: python

    # Turn on the night light
    base_station.set_night_light_on()

    # Turn off the night light
    base_station.set_night_light_off()

    # Set the brightness of the night light
    base_station.set_night_light_brightness(200)


Supported Devices
-----------------
If you have a different model, please feel free to contribute by reporting your results.

+-------------------------+---------------+------------+-----------------+
| Model                   |  Tested by    |   Status   | Results/Issues  |
+=========================+===============+============+=================+
| Arlo 1st Generation     | @tchellomello | working/ok |     N/A         |
+-------------------------+---------------+------------+-----------------+
| Arlo 2st Generation     | @tchellomello | working/ok |     N/A         |
+-------------------------+---------------+------------+-----------------+


Contributing
------------
See more at CONTRIBUTING.rst_.
