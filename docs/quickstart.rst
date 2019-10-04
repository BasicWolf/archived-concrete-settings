The Basics
==========

In this chapter we cover the essentials of Concrete Settings.

Defining settings
-----------------

As you have probably guessed, defining settings starts
by subclassing the :class:`Settings <concrete_settings.Settings>`
class.
The setting attributes are descriptors of type
:class:`Setting <concrete_settings.Setting>`.
The catch is that a developer does not need
to declare each setting explicitly.
For example, the following two definitions are identical:

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

But wouldn't you agree that the first definition
is easier to comprehend than the second one?
The first definition looks like a boring class attribute
with a sphinx-style documentation above it.
At the same time, all the required details are extracted and processed,
and a substitute ``Setting`` attribute is created.
In fact, Concrete Settings is even able to guess a setting
type automatically:

.. code-block::

   from concrete_settings import Settings

   class AppSettings(Settings):
       DEBUG = True

   print(AppSettings.DEBUG.type_hint)
   # >>> <class 'bool'>

The magic behind the scenes is happening in the metaclass
:class:`SettingsMeta <concrete_settings.concrete_settings.SettingsMeta>`.
In a nutshell, if a field looks like a setting, but is not explicitly
defined (e.g. ``DEBUG = True``), a corresponding instance of
:class:`Setting <concrete_settings.Setting>` is created instead.

We will `later <automated_settings_>`_ discuss the setting creation rules in-depth.
For now please accept that Concrete Settings way of declaring
basic settings is by omitting the ``Setting(...)`` call at all.
Ideally a setting should be declared with a type annotation and documentation
as follows:

.. code-block::

   class AppSettings(Settings):

       #: Maximum number of parallel connections.
       #: Note that a high number of connections can slow down
       #: the program.
       MAX_CONNECTIONS: int = 10

You can also declare a setting as a method, similar to
a Python read-only :class:`property`:

.. code-block::

   from concrete_settings import Settings, setting

   class DBSettings(Settings):
       USER: str = 'alex'
       PASSWORD: str  = 'secret'
       SERVER: str = 'localhost'
       PORT: int = 5432

       @setting
       def URL(self) -> str:
           """Database connection URL"""
           return f'postgresql://{self.USER}:{self.PASSWORD}@{self.SERVER}:{self.PORT}'

   print(DBSettings().URL)
   # >>> postgresql://alex:secret@localhost:5432


Before we go further, let's take a look at the contents of a Setting object.
Each implicitly or explicitly defined setting consists of a
**name**, **default value**, a **type hint**,
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
* **Validators** is a list of callables which validate the value of the setting.
* **Documentation** is a multi-line doc string intended for the end user.


Reading settings from files and environment
-------------------------------------------

After a Settings object has initialized successfully it can be updated
with values from different :ref:`api_sources`, such as :class:`YAML
<concrete_settings.sources.YamlSource>`, :class:`JSON
<concrete_settings.sources.JsonSource>` files,
:class:`enironmental variables <concrete_settings.sources.EnvVarSource>`
or a plain Python ``dict``.

And if none of the above fits your needs, check out [TODO]
:mod:`sources API <concrete_settings.sources>` for creating
a required settings source.

To update a settings object, call :meth:`<concrete_settings.Settings.update>`.
For example, to update the settings from a JSON file:


.. code-block:: json

   {
       "ADMIN_EMAIL": "alex@my-super-app.io"
       "ALLOWED_HOSTS": ["localhost", "127.0.0.1", "::1"]
   }

.. code-block::

   from concrete_settings import Settings
   from typing import List

   class AppSettings(Settings):
       ADMIN_EMAIL: str = 'admin@example.com'
       ALLOWED_HOSTS: List = [
           'localhost',
           '127.0.0.1',
       ]

   app_settings = AppSettings()
   app_settings.update('/path/to/settings.json')

   print(app_settings.ADMIN_EMAIL)
   # >>> alex@my-super-app.io




Validation
----------

  :class:`Validator <concrete_settings.validators.Validator>` objects


Type hint
---------



Nested settings
---------------

What makes it very fascinating and maybe a bit confusing is
that :class:`Settings <concrete_settings.Settings>` is a
subclass of :class:`Setting <concrete_settings.Setting>`!

In practice, this allows you to

.. _automated_settings:

Automated Setting creation
..........................

**Name**

Every attribute with **name** written in upper case
is considered a potential Setting.
The exceptions are attributes starting with underscore:

.. code-block::

   class AppSettings(Settings):

       debug = True   # not considered a setting

       _DEBUG = True  # not considered a setting

       DEBUG = True   # considered a setting

**Default value**

The *default value* is the initial value of the attribute:

.. code-block::

   class AppSettings(Settings):
       DEBUG = True  # the default value is `True`

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

..  code-block::

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
