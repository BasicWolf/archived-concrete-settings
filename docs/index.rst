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
for both developer and an end-user:

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
       from files, environmental variables
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

This flow perfectly fits for

* A web application backend. Think of Django or Flask application
  and all the settings required to start it up.
* A rich feed-execute-output tools like Sphinx documentation.

Sounds interesting?
Then you are very welcome to ConcreteSettings documentation!


.. contents:: Table of Contents
   :depth: 3


Defining Settings
-----------------

As you have probably guessed, defining settings starts
by subclassing the :class:`Settings <concrete_settings.Settings>`
class.
The setting attributes are descriptors of type
:class:`Setting <concrete_settings.Setting>`.
However a developer does not need to declare each setting explicitly.
For example, the following two definitons are identical:

.. code-block::

   from concrete_settings import Settings

   class AppSettings(Settings):

       #: Turns debug mode on/off
       DEBUG: bool = True

.. code-block::

   from concrete_settings import Settings, Setting
   from concrete_settings.validators import ValueTypeValidator

   class AppSettings(Settings):
       DEBUG = Setting(
           True,
           type_hint=bool,
           validators=(ValueTypeValidator(), ),
           doc="Turns debug mode on/off"
       )

This behaviour does not truly comply with the Zen of Python:

  *Explicit is better than implicit*.

However the first definition
is clearly simpler and easier to comprehend than the second one.
In fact, Concrete Settings is even able to guess the settings
types automatically:

.. code-block::

   from concrete_settings import Settings

   class AppSettings(Settings):
       DEBUG = True

   print(AppSettings.DEBUG.type_hint)
   # <class 'bool'>

The magic behind the scenes is happening in the metaclass
:class:`SettingsMeta <concrete_settings.concrete_settings.SettingsMeta>` .
In a nutshell, if a field looks like a setting, but is not explicitly
defined (e.g. ``DEBUG = True``), a corresponding instance of
:class:`Setting <concrete_settings.Setting>` is created instead.

We will later discuss the setting creation rules in-depth.
For now please accept that Concrete Settings way of declaring
setting is by omitting the ``Setting(...)`` call at all.
Ideally a setting should be provided a type and documentation
as follows:

.. code-block::

   class AppSettings(Settings):

       #: Maximum number of parallel connections.
       #: Note that a high number of connections can slow down
       #: the program.
       MAX_CONNECTIONS: int = 10


Setting attributes
..................

Each setting consists of a **name**, **default value**, a **type hint**,
a **list of validators** and **documentation**:

.. uml::
   :align: center

   @startuml
   (Default value) --> (Setting)
   (Type hint) --> (Setting)
   (Validators) --> (Setting)
   (Documentation) --> (Setting)

   note left of (Setting) : NAME
   @enduml

* **Default value** is a setting's initial value.
* **Type hint** is a setting type. It is called a hint, since there is no
  behavior bound to it per se. However a **validator** like the built-in
  :class:`ValueTypeValidator <concrete_settings.validators.ValueTypeValidator>`
  can use the *type hint* to check whether the setting value corresponds
  to the given type.
* **Validators** is a list of
  :class:`Validator <concrete_settings.validators.Validator>` objects
  which are used to validate the final value of the setting.
* **Documentation** is a multi-line doc string intended for the end user.


Automated Setting creation
..........................

Name
''''

Every attribute with **name** written in upper case
is considered a potential Setting.
The exceptions are attributes starting with underscore:

.. code-block::

   class AppSettings(Settings):

       debug = True   # not considered a setting

       _DEBUG = True  # not considered a setting

       DEBUG = True   # considered a setting

Default value
'''''''''''''

The *default value* is value of the attribute.

If an attribute is not type-annotated, a *type hint* is computed
by calling ``type()`` on the default value. The recognized types
are declared in
:attr:`GuessSettingType.KNOWN_TYPES <concrete_settings.types.GuessSettingType.KNOWN_TYPES>` field.
If the type is not recognized, the type hint is set to :data:`typing.Any`.

.. code-block::

   class AppSettings(Settings):

       DEBUG = True  # default value `True`, type `bool`

       MAX_SPEED: int = 300   # default value `300`, type `int`

Combining settings
..................

.. uml::

   @startuml
   (Feature X settings) --> (Settings)
   (Feature Y settings) --> (Settings)
   (Feature Z settings) --> (Settings)
   @enduml



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
