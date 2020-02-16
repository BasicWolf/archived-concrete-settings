Concrete Settings
#################

.. image:: https://travis-ci.org/BasicWolf/concrete-settings.svg?branch=master
    :target: https://travis-ci.org/BasicWolf/concrete-settings

.. image:: https://basicwolf.github.io/concrete-settings/_static/img/codestyle_black.svg
    :target: https://github.com/ambv/black

.. image:: https://basicwolf.github.io/concrete-settings/_static/img/mypy_checked.svg
   :target: https://github.com/python/mypy

Welcome
=======

**Concrete Settings** is a small Python library which facilitates
configuration management in applications.

The settings definition DSL aims to be simple and easy readible.
It is designed with these concepts in mind:

* Settings are defined in classes.
* Settings are documented.
* Settings are type-annotated and validated.
* Settings can be mixed and nested.
* Settings can be read from any sources: Python dict, yaml, json, environmental variables etc.

Here is a small example of Settings class with one
boolean setting ``DEBUG``. A developer defines the
settings in application code, while an end-user
stores the configuration in a YAML file:

.. code-block:: python

   from concrete_settings import Settings

   class AppSettings(Settings):

       #: Turns debug mode on/off
       DEBUG: bool = False
       ..
   app_settings = AppSettings()
   app.read('/path/to/user/settings.yml')
   app_settings.is_valid(raise_exception=True)

While the end-user could set the values in a YAML file:

.. code-block:: yaml

   # settings.yml

   DEBUG: true

Accessing settings:

.. code-block:: pycon

   >>>  print(app_settings.DEBUG)

   True


Install Concrete Settings
-------------------------

.. code-block:: bash

   pip install concrete-settings
