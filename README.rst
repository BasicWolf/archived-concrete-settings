Concrete Settings
#################

.. image:: https://travis-ci.org/BasicWolf/concrete-settings.svg?branch=master
    :target: https://travis-ci.org/BasicWolf/concrete-settings

.. image:: https://basicwolf.github.io/concrete-settings/_static/img/codestyle_black.svg
    :target: https://github.com/ambv/black

.. image:: https://basicwolf.github.io/concrete-settings/_static/img/mypy_checked.svg
   :target: https://github.com/python/mypy

.. image:: https://basicwolf.github.io/concrete-settings/_static/img/pyup_scanned.svg
   :target:: https://pyup.io


Welcome to Concrete Settings
============================

**Concrete Settings** is a Python library which facilitates
configuration management in big and small projects.

The library was born out of necessity to manage a huge
decade-old Django-based SaaS solution with more than two hundred
different application settings scattered around ``settings.py``.
*What does this setting do?*
*What type is it?*
*Why does it have such a weird format?*
*Is this the final value, or it changes somewhere on the way?*
Sometimes developers spent *hours* seeking answers to these
questions.

Concrete Settigns tackles these problems altogether.
It was designed to be developer and end-user friendly.
The settings are defined via normal Python code with few
tricks which significantly improve readability
and maintainability.

Take a look at a small example of Settings class with one
boolean setting ``DEBUG``. A developer defines the
settings in application code, while an end-user
chooses to store the configuration in a YAML file:

.. code-block:: python

   # settings.py

   from concrete_settings import Settings

   class AppSettings(Settings):

       #: Turns debug mode on/off
       DEBUG: bool = False


   app_settings = AppSettings()
   app_settings.update('/path/to/user/settings.yml')
   app_settings.is_valid(raise_exception=True)

.. code-block:: yaml

   # settings.yml

   DEBUG: true


Accessing settings:

.. code-block:: pycon

   >>>  print(app_settings.DEBUG)
   True

   >>> print(AppSettings.DEBUG.__doc__)
   Turns debug mode on/off


Settings are **defined in classes**. Python mechanism
of inheritance and composition apply here, so settings can be **mixed** (multiple inheritance)
and be **nested** (settings as class fields).
Settings are **type-annotated** and are **validated**.
Documentation matters! Each settings can be documented in Sphinx-style comments ``#:`` written
above its definition.
An instance of ``Settings`` can be updated i.e. read from any kind of source:
YAML, JSON or Python files, environmental variables, Python dicts, and you can add more!

Finally, Concrete Settings comes with batteries like Django 3.0 support out of the box.

Concrete Settings are here to improve configuration handling
whether you are starting from scratch, or dealing with an
old legacy Cthulhu.
Are you ready to try it out?

``pip install concrete-settings`` and welcome to the `documentation <https://basicwolf.github.io/concrete-settings>`_!

Show me more
============

So, you are a kind of a developer who expects more show cases in a ``README``?
Let's see!

Never miss an invalid value via validators
------------------------------------------

For example, the default *type validator* works like this:

.. code-block:: python

   from concrete_settings import Settings

   class AppSettings(Settings):
       SPEED: int = 'abc'

   app_settings = AppSettings()
   print(app_settings.is_valid(raise_exception=False))
   print(app_settings.errors)

Output:

.. code-block::

   False
   {'SPEED': ["Expected value of type `<class 'int'>` got value of type `<class 'str'>`"]}


Easily warn about deprecation via behavior
------------------------------------------

Use **behaviors** to control settings during their *initialization*, *validation*,
*reading* and *writing* operations:

.. code-block:: python

   from concrete_settings import Settings, Setting
   from concrete_settings.contrib.behaviors import deprecated

   class AppSettings(Settings):
       MAX_SPEED: int = 30 @deprecated

   app_settings = AppSettings()
   app_settings.is_valid()

Running this code with ``python -Wdefault`` yields:

.. code-block::

   DeprecationWarning: Setting `MAX_SPEED` in class `<class '__main__.AppSettings'>` is deprecated.


Group settings and nest them
----------------------------

Different settings in a huge setting file?
Why have those stupid ``GROUP_PREFIXES_...``?
Instead group and nest settings:

.. code-block:: python

   from concrete_settings import Settings

   class DBSettings(Settings):
       USER = 'alex'
       PASSWORD  = 'secret'
       SERVER = 'localhost@5432'

   class CacheSettings(Settings):
       ENGINE = 'DatabaseCache'
       TIMEOUT = 300

   class LoggingSettings(Settings):
       LEVEL = 'INFO'
       FORMAT = '%(asctime)s %(levelname)-8s %(name)-15s %(message)s'


   class AppSettings(Settings):
       DB = DBSettings()
       CACHE = CacheSettings()
       LOG = LoggingSettings()

   app_settings = AppSettings()
   app_settings.is_valid()  # also invokes DB, CACHE and LOG validation
   print(app_settings.LOG.LEVEL)

There is more
-------------

There is even more for you to discover in
`documentation <https://basicwolf.github.io/concrete-settings>`_,
and there is more to come. **Your** contribution, be it
a *bug report*, *pull request*, *suggested feature*,
*comments* and *criticism* are very welcome!

Awesome configuration projects
==============================

Concrete Settings is not the first and surely not the last library to handle
configuration in Python projects.

* `goodconf <https://github.com/lincolnloop/goodconf/>`_
  - Define configuration variables and load them from environment or
  JSON/YAML file. Also generates initial configuration files and
  documentation for your defined configuration.

* `profig <https://profig.readthedocs.io>`_
  - is a straightforward configuration library for Python.
  Its objective is to make the most common tasks of configuration
  handling as simple as possible.

* `everett <https://everett.readthedocs.io/en/latest/>`_
  - is a Python configuration library with the following goals:
  flexible configuration from multiple configured environments;
  easy testing with configuration and easy documentation of configuration
  for users.

* `python-decouple <https://github.com/henriquebastos/python-decouple>`_
  - strict separation of settings from code. Decouple helps you to organize
  your settings so that you can change parameters without having to redeploy
  your app.

Why should you trust Concrete Settings instead of picking some other library?
Concrete Settings tries to make configuration definition, processing and maintenance smooth and transparent for developers. Its implicit definition syntax eliminates extra code and allows you to focus on  what is important.
