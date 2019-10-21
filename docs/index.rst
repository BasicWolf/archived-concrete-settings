Welcome to ConcreteSettings
===========================

**WARNING!** ConcreteSettings is currently under development!
There is no stable, not even an alpha version available at the moment.

ConcreteSettings is a Python library which facilitates startup
configuration management in applications.

A minimal developer-facing settings class might look like this:

.. code-block:: python

   from concrete_settings import Settings

   class AppSettings(Settings):

       #: Turns debug mode on/off
       DEBUG: bool = True

   app_settings = AppSettings()
   app.read('/path/to/user/settings.yml')
   app_settings.is_valid(raise_exception=True)

While the end-user could set the values in a YAML file:

.. code-block:: yaml

   # settings.yml

   DEBUG: off

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
       via ConcreteSettings
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


.. toctree::
   :maxdepth: 2

   quickstart


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
