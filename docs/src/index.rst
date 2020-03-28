Welcome to Concrete Settings
============================

.. contents:: :depth: 1

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
controls the final configuration in a YAML file:

.. testcode:: index-example
   :hide:

   with open('/tmp/settings.yml', 'w') as f:
       f.write('DEBUG: true')

   from concrete_settings import Settings

   class AppSettings(Settings):

       #: Turns debug mode on/off
       DEBUG: bool = False


   app_settings = AppSettings()
   app_settings.update('/tmp/settings.yml')
   app_settings.is_valid(raise_exception=True)

   print(app_settings.DEBUG)

.. testoutput:: index-example
   :hide:

   True


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

In a nutshell:

.. uml::

   @startuml
   :Developer: as Dev
   :Application User: as User
   (.yaml) as (yaml_source)
   (.json) as (json_source)
   (.py) as (py_source)
   (Environmental Variables) as (envvar)

   note top of User
       **User** sets configuration
       in files, environmental variables
       and other **sources**.
   end note

   note top of Dev
       **Developer** defines configuration
       via Concrete Settings
   end note

   User ==> (yaml_source)
   User ==> (json_source)
   User ==> (envvar)
   User ==> (py_source)
   User ==> (...)

   Dev ==> (Settings)

   (yaml_source) .. (Sources)
   (json_source) .. (Sources)
   (envvar) .. (Sources)
   (...) .. (Sources)

   note "Verify definition structure" as note_verify
   note "Update Settings from sources" as note_update
   note "Validate values" as note_validate

   note_update <== (Sources)

   (Settings) .. note_verify
   note_verify ..> note_update
   note_update .. note_validate
   note_validate ..> (Application)

   @enduml

This flow is a perfect fit for

* A web application backend. Think of Django or Flask application
  and all the settings required to start it up.
* A rich feed-execute-output tools like Sphinx documentation.

Are you ready to try it out?
Then you are very welcome to Concrete Settings documentation!


Installation
============

Python Version
--------------

We recommend using the latest version of Python 3.
Concrete Settings supports Python 3.6 and newer.

With pip:

.. code-block:: bash

   pip install concrete-settings

Dependencies
------------

These distributions will be installed automatically when installing Concrete Settings:

* `Typeguard <https://github.com/agronholm/typeguard>`_  provides runtime type checking and allows validating settings values types.
* `Sphinx <https://www.sphinx-doc.org/en/master/>`_ allows documenting settings in developer-friendly way - in comments above settings definitions.
* `Typing Extensions <https://github.com/python/typing/tree/master/typing_extensions>`_ provides typing hints backports to Python 3.6.

Optional dependencies
---------------------

These distributions will not be installed automatically. Concrete Settings will detect and use them if you install them.

* `PyYAML <https://pyyaml.org/>`_ allows reading settings from YAML sources.


Install Concrete Settings
-------------------------

.. code-block:: bash

   pip install concrete-settings

Source
------

The source is available at `<https://github.com/basicwolf/concrete-settings>`_.

Contributions are warmly welcomed!

Documentation
=============

.. toctree::
   :maxdepth: 2

   basic_concepts
   startup
   advanced
   batteries

API Reference
=============

If you are looking for information on a specific function, class or
method, this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
