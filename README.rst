Concrete Settings
#################

.. image:: https://travis-ci.org/BasicWolf/concrete-settings.svg?branch=master
    :target: https://travis-ci.org/BasicWolf/concrete-settings

.. image:: https://basicwolf.github.io/concrete-settings/_static/img/codestyle_black.svg
    :target: https://github.com/ambv/black

.. image:: https://basicwolf.github.io/concrete-settings/_static/img/mypy_checked.svg
   :target: https://github.com/python/mypy

Welcome to Concrete Settings
============================

**Concrete Settings** is a Python library which facilitates
configuration management in big and small programs.

The project was born out of necessity to manage a huge
decade-old Django-based SaaS solution with more than two hundred
different application settings scattered around ``settings.py``.
*What does this setting do?*
*What type is it?*
*Why does it have such a weird format?*
*Is this the final value, or it changes somewhere on the way?*
Sometimes developers spent *hours* seeking answers to these
questions.

**Concrete Settigns** tackles these problems altogether.
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


As you can see, settings are **defined in classes**. Python mechanism
of inheritance and nesting apply here, so settings can be **mixed** (multiple inheritance)
and be **nested** (settings as class fields).
Settings are **type-annotated** and are **validated**.
Documentation matters! Each settings can be documented in Sphinx-style comments ``#:`` written
above its definition.
An instance of ``Settings`` can be updated i.e. read from any kind of source:
YAML, JSON or Python files, environmental variables, Python dicts, and you can add more!

Finally, **Concrete Settings** comes with batteries like Django 3.0 support out of the box.

Concrete Settings are here to improve configuration handling
whether you are starting from scratch, or dealing with an
old legacy Cthulhu.
Are you ready to try it out?

``pip install concrete-settings`` and welcome to the `documentation <https://basicwolf.github.io/concrete-settings>`_!
