Welcome to Concrete Settings
============================

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


Concrete Settings aims to provide a conveniet way to
define and use application startup settings
for developers and an end-users:

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

   note "Read from sources" as note_read_settings

   Dev ==> (Settings)

   (yaml_source) .. note_read_settings
   (json_source) .. note_read_settings
   (envvar) .. note_read_settings
   (...) .. note_read_settings
   note_read_settings ..> (Settings)

   note "Verify definition structure" as note_verify
   note "Validate values" as note_validate

   (Settings) .. note_verify
   note_verify ..> (Application)
   (Settings) .. note_validate
   note_validate ..> (Application)

   @enduml

This flow is a perfect fit for

* A web application backend. Think of Django or Flask application
  and all the settings required to start it up.
* A rich feed-execute-output tools like Sphinx documentation.

Sounds interesting?
Then you are very welcome to ConcreteSettings documentation!


Installation
============

TODO

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
