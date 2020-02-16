Concrete Settings
#################

.. image:: https://travis-ci.org/BasicWolf/concrete-settings.svg?branch=master
    :target: https://travis-ci.org/BasicWolf/concrete-settings

.. image:: https://basicwolf.github.io/concrete-settings/_static/img/codestyle_black.svg
    :target: https://github.com/ambv/black

.. image:: https://basicwolf.github.io/concrete-settings/_static/img/mypy_checked.svg
   :target: https://github.com/python/mypy

.. contents:: :depth: 2


Welcome
=======

**Concrete Settings** is a small Python library which facilitates
configuration management in big and small applications.

The settings definition DSL aims at being simple and easy readible.
Settings are:

* Defined in classes
* Type-annotated and validated
* Mixable and nestable
* Can be read from any sources: Python dict, yaml, json, environmental variables etc.
* Documentation matters.

Here is a small example of Settings class with one
boolean setting ``DEBUG``. A developer defines the
settings in application code, while an end-user
stores the configuration in a YAML file:

.. code-block:: python

   # settings.py

   from concrete_settings import Settings

   class AppSettings(Settings):

       #: Turns debug mode on/off
       DEBUG: bool = False


   app_settings = AppSettings()
   app_settings.update('/path/to/user/settings.yml')
   app_settings.is_valid(raise_exception=True)

While the end-user could set the values in a YAML file:

.. code-block:: yaml

   # settings.yml

   DEBUG: true

Accessing settings:

.. code-block:: pycon

   >>>  print(app_settings.DEBUG)

   True

   >>> print(AppSettings.DEBUG.__doc__)

   Turns debug mode on/off

Install Concrete Settings
-------------------------

.. code-block:: bash

   pip install concrete-settings
