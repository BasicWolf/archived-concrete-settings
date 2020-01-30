.. _startup:

Start me up
###########

Scratch
=======

An extremely short guide to start using Concrete Setting in your application.

I. Define Settings
------------------

As a *developer* of an application, define the settings:

For example, ``my_app/settings_definition.py`` file:

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

   from .settings_definition import ApplicationSettings


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

   DEBUG: true


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

III. Remember to test settings object definition
------------------------------------------------

.. code-block::

    # we love pytest!

    from my_app.settings_definition import ApplicationSettings

    def test_settings_definiton():
        ApplicationSettings()

That's it! You are ready to start using Concrete Settings in your programs!


Django Projects
===============

Concrete Settings is shipped with batteries which help bootstrapping
settings in a legacy or a brand new Django project.
First, there is :class:`Django30Settings <concrete_settings.contrib.frameworks.django30.Django30Settings>`
class which reflects Django's `global_settings` definitions.

Django 3.0
----------


