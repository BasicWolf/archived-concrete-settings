.. _startup:

Start me up
###########

Scratch
=======

An extremely short guide to start using ConcreteSetting in your application.

I. Define Settings
------------------

As a *developer* of an application, define the settings
in a file *inside* your application.

For example, ``my_app/app_settings.py`` file:

.. testcode:: start-me-up

   from concrete_settings import Settings

   class ApplicationSettings(Settings):
       #: Turns on / off debug mode
       DEBUG: bool = False

II. Think of an end-user
------------------------

Provide a conventient way of entering the application settings to an end-user.
For example  via a ``.yaml`` file passed as a command-line argument:


.. code-block::

   # my_app/main.py

   import os
   import sys

   from .app_settings import ApplicationSettings


   def main():
       """Usage:


       python main.py /path/to/settings.yaml
       """
       settings = ApplicationSettings()
       if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
           print(f'Reading settings from {sys.argv[1]}')
           settings.update(sys.argv[1])

       # validate the settings,
       # raise exception if something is invalid
       settings.is_valid(raise_exception=True)

       # start application with settings
       ...
       if settings.DEBUG:
           ...


.. code-block:: yaml

   # settings.yaml

   debug: true


.. testcode:: start-me-up
   :hide:

   import os
   import sys

   def main():
       settings = ApplicationSettings()
       if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
           print(f'Reading settings from {sys.argv[1]}')
           settings.update(sys.argv[1])

       # validate the settings,
       # raise exception if something is invalid
       settings.is_valid(raise_exception=True)

       # start application with settings
       ...
       if settings.DEBUG:
           ...

   main()

III. Remember to unit-test settings object initialization
---------------------------------------------------------

.. code-block::

    # we love pytest!

    from my_app.app_settings import ApplicationSettings

    def test_smoke_the_settings():
        ApplicationSettings()


New Django Projects
===================

from concrete_settings.contrib.conf import django30


