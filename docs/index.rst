.. Concrete Settings documentation master file, created by
   sphinx-quickstart on Sun Apr 14 18:28:20 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Concrete Settings
============================

**WARNING!** Concrete Settings is currently in development!
There is no stable, not even pre-alpha version currently available.

Does your application has tens or hundreds of settings
scattered around files and environmental variables?
Does dependency management becomes unberable?
Are you having problems at startup, since it's hard
to follow where the values are coming from and there is no verifaction?

**Concrete Settings** was created to solve all these issues and more!

Concrete Settings is a Python library which facilitates configuration management in large projects.

.. toctree::
   :maxdepth: 2
   :caption: Contents:



With Concrete Settings a developer can declare the settings in different classes
and then combine them by composition, inheritance or both!
Each setting carries the information and functionality
allowing to initialize, read and validate it at any point of time.

Sounds unbelievable? Let's discover together by looking at some examples:


.. code-block:: pycon

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

The settings are


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


Composition
-----------





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
