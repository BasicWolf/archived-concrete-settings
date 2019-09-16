.. Concrete Settings documentation master file, created by
   sphinx-quickstart on Sun Apr 14 18:28:20 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Concrete Settings
============================

**WARNING!** Concrete Settings is currently under development!
There is no stable, not even an alpha version available at the moment.

Does your application has tens or hundreds of settings
scattered around files and environmental variables?
Is dependency management unberable?
Are you having problems at startup, since it's hard
to follow where the configuration values are coming
from and there is no unified way to verify them?

**Concrete Settings** was created to solve all these issues and more!

Concrete Settings is a Python library which facilitates configuration management
in applications. Sounds unbelievable? Let's discover together by looking at some
examples!

.. contents:: Table of Contents


Hello world
...........

.. code-block:: python

   from concrete_settings import Settings

   class AppSettings(Settings):

       #: Turns debug mode on/off
       DEBUG: bool = True

   app_settings = AppSettings()
   app_settings.is_valid(raise_exception=True)

   print(app_settings.DEBUG)
   >>> True


This example demonstrates the basic concepts of Concrete Settings.
We define a settings class with a setting called ``DEBUG``.
Its type is ``bool`` and the default value is ``True``.
The docstring of the setting is defined in a ``#:`` comment block.

The equivalent verbose form is:

.. code-block:: python

  from concrete_settings import Settings, Setting
  from concrete_settings.validators import ValueTypeValidator

  class AppSettings(Settings):
      DEBUG = Setting(
          True,
          type_hint=bool,
          validators=(ValueTypeValidator(), ),
          doc="Turns debug mode on/off"
      )

Sounds intriguing? We have to go deeper!


Basic workflow
..............





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
