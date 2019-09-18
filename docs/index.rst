.. ConcreteSettings documentation master file, created by
   sphinx-quickstart on Sun Apr 14 18:28:20 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

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

While the end-user would set the values in a YAML file:

.. code-block:: yaml

   # super-application-config.yml

   DEBUG: off

Sounds interesting?
Then you are very welcome to ConcreteSettings documentation!


.. contents:: Table of Contents


Use cases
---------

ConcreteSettings provides a one-way configuration management:


.. uml::

   @startuml
   :Developer: as Dev
   :User: as User
   (.yaml) as (yaml-source)
   (.json) as (json-source)
   (.py) as (py-source)
   (Environmental Variables) as (envvar)

   note top of User
       **User** interacts with configuration
       via **sources**:
       files, environmental variables etc.
   end note

   note top of Dev
       **Developer** defines configuration
       via ConcreteSettings
   end note

   User ==> (yaml-source)
   User ==> (json-source)
   User ==> (envvar)
   User ==> (py-source)
   User ==> (...)

   Dev ==> (Settings)
   (yaml-source) --> (Settings)
   (json-source) --> (Settings)
   (envvar) --> (Settings)
   (...) --> (Settings)

   note "Verify settings structure" as N10
   (Settings) .. N10
   N10 .. (Verify)


   @enduml

* A web application backend. Think of Django or Flask application
  and all the settings required to start it up.
* A

Concrete Settings provides a simple way to define the start-up
configuration of an application

Could you name the favourite setting of all the developers around the globe?
I think it is the ``DEBUG`` flag. Let's define a settings class for an
application:

   print(app_settings.DEBUG)
   >>> True


This example demonstrates the basic concepts of Concrete Settings.
We define a settings class with a setting called ``DEBUG``.
Its type is ``bool`` and the default value is ``True``.
The docstring of the setting is defined in a ``#:`` comment block.

Does the end user has to see all of this? Of course not!
A user can adjust the values in a configuration-friendly
file be it YAML, JSON, Environmental variables or
just plain Python module.:

Sounds intriguing? We have to go deeper!


Internal workflow
.................



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



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
