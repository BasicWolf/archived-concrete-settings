Quickstart
==========

In this chapter we cover the essentials of Concrete Settings.

.. contents::
   :local:

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
           doc="Turns debug mode on/off",
       )

Though this does not truly comply with the Zen of Python

  *Explicit is better than implicit*.

wouldn't you agree that the first definition
is easier to comprehend than the second one?
The first definition looks like a boring class attribute
with a sphinx-style documentation above it.
At the same time, all the required details are extracted and processed,
and a substitute ``Setting`` attribute is created.

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

.. testcode:: quickstart-define-setting

   from concrete_settings import Settings

   class AppSettings(Settings):

       #: Maximum number of parallel connections.
       #: Note that a high number of connections can slow down
       #: the program.
       MAX_CONNECTIONS: int = 10

You can also declare a setting as a method, similar to
a Python read-only :class:`property`:

.. testcode:: quickstart-define-property

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

Output:

.. testoutput:: quickstart-define-property

   postgresql://alex:secret@localhost:5432


Before we go further, let's take a look at the contents of a Setting object.
Each implicitly or explicitly defined setting consists of a
**name**, **default value**, a **type hint**,
lists of **validators** and **behaviors**
and **documentation**:

.. uml::
   :align: center

   @startuml
   (Default value) --> (Setting)
   (Type hint) --> (Setting)
   (Validators) --> (Setting)
   (Behaviors) --> (Setting)
   (Documentation) --> (Setting)

   note left of (Setting) : NAME
   @enduml

* **Default value** is a setting's initial value.
* **Type hint** is a setting type. It is called a hint, since it carries no
  meaning on its own. However a **validator** like the built-in
  :class:`ValueTypeValidator <concrete_settings.validators.ValueTypeValidator>`
  can use the *type hint* to check whether the setting value corresponds
  to the given type.
* **Validators** is a collection of callables which validate the value of the setting.
* **Behaviors** is a collection of :class:`SettingBehavior <concrete_settings.behaviors.SettingBehavior>`
  objects which modify the behavior of the setting during its *get* and *set* invocations and
  its owner *initialization*.
* **Documentation** is a multi-line doc string intended for the end user.


Reading settings
----------------

After a Settings object has initialized successfully it can be updated
with values from different :ref:`api_sources`, such as
:class:`YAML <concrete_settings.contrib.sources.YamlSource>` or
:class:`JSON <concrete_settings.contrib.sources.JsonSource>`
files,
:class:`enironmental variables <concrete_settings.contrib.sources.EnvVarSource>`
or a plain Python dict.

And if none of the above fits your needs, check out
:mod:`sources API <concrete_settings.sources>` for creating
a required settings source.

Updating is done by calling :meth:`Settings.update(source) <concrete_settings.Settings.update>`.
For example, to update the settings from a JSON file:


.. code-block:: json

   {
       "ADMIN_EMAIL": "alex@my-super-app.io",
       "ALLOWED_HOSTS": ["localhost", "127.0.0.1", "::1"]
   }

.. testsetup:: quickstart-json-source

   with open('/tmp/cs-quickstart-settings.json', 'w') as f:
       f.write('''
           {
              "ADMIN_EMAIL": "alex@my-super-app.io",
              "ALLOWED_HOSTS": ["localhost", "127.0.0.1", "::1"]
           }
       ''')

.. testcode:: quickstart-json-source

   from concrete_settings import Settings
   from concrete_settings.contrib.sources import JsonSource
   from typing import List

   class AppSettings(Settings):
       ADMIN_EMAIL: str = 'admin@example.com'
       ALLOWED_HOSTS: List = [
           'localhost',
           '127.0.0.1',
       ]

   app_settings = AppSettings()
   app_settings.update('/tmp/cs-quickstart-settings.json')

   print(app_settings.ADMIN_EMAIL)

Output:

.. testoutput:: quickstart-json-source

   alex@my-super-app.io

.. testcleanup:: quickstart-json-source

   import os
   os.remove('/tmp/cs-quickstart-settings.json')


.. _quickstart_validation:

Validation
----------

When Settings values have been finaly loaded, it is time
to validate each and all settings' values altogether.

A Settings object validates its setting-fields and itself when
:meth:`Settings.is_valid() <concrete_settings.Settings.is_valid()>`
is called for the first time.
Validation consists of two stages:

1. Each :class:`validator <concrete_settings.validators.Validator>`
   of every setting-field's ``.validators`` list is called
   to validate the setting-field's value.

2. :meth:`Settings.validate() <concrete_settings.Settings.validate>` is called.
   It is indtended to validate the Settings object as a whole.

All validation errors are collected and stored in :meth:`Settings.errors <concrete_settings.Settings.errors>`

.. testcode:: quickstart-validation

   from concrete_settings import Settings, Setting
   from concrete_settings.exceptions import SettingsValidationError

   def not_too_fast(speed, **kwargs):
       if speed > 100:
           raise SettingsValidationError(f'{speed} is too fast!')

   def not_too_slow(speed, **kwargs):
       if speed < 10:
           raise SettingsValidationError(f'{speed} is too slow!')

   class AppSettings(Settings):
       SPEED: int = Setting(50, validators=(not_too_fast, not_too_slow))

   app_settings = AppSettings()
   app_settings.SPEED = 5

   print(app_settings.is_valid())
   print(app_settings.errors)

Output:

.. testoutput:: quickstart-validation

   False
   {'SPEED': ['5 is too slow!']}


Type hint
---------

Type hint is a setting type.
It is intended to be used by validators, like the built-in
:class:`ValueTypeValidator <concrete_settings.validators.ValueTypeValidator>`
to validate a setting's value.
Otherwise it carries no meaning and is just a valid Python value.

The :class:`ValueTypeValidator <concrete_settings.validators.ValueTypeValidator>`
is a :ref:`default validator <advanced_validators>` for settings which have no validators defined explicitly:


.. testcode:: quickstart-type-hint

   from concrete_settings import Settings

   class AppSettings(Settings):
       SPEED: int = 'abc'

   app_settings = AppSettings()
   print(app_settings.is_valid())
   print(app_settings.errors)

.. testoutput:: quickstart-type-hint

   False
   {'SPEED': ["Expected value of type `<class 'int'>` got value of type `<class 'str'>`"]}


.. _quickstart_behavior:

Setting Behavior
----------------

Imagine that you want to notify the users that a setting is now deprecated.
You would like to raise a warning when settings are initialized and
every time the setting is being read.

A straightforward way to do this is by sublassing the
:class:`Setting <concrete_settings.Setting>` class and overriding
:meth:`Setting.__get__() <concrete_settings.Setting.__get__>`.

Another way would be using the supplied Settings Behavior mechanism.
For example, the built-in :class:`deprecated <concrete_settings.contrib.behaviors.deprecated>`
validator adds the :class:`DeprecatedValidator <concrete_settings.contrib.validators.DeprecatedValidator>` to the setting looks like this:

.. testcode:: quickstart-behavior:

   from concrete_settings import Settings
   from concrete_settings.contrib.behaviors import deprecated

   class AppSettings(Settings):
       MAX_SPEED: int = 30 @deprecated

   app_settings = AppSettings()

If Python warnings are enabled (e.g. ``python -Wdefault``), you would
get the warning in stderr:


.. code-block:: none

   DeprecationWarning: Setting `MAX_SPEED` in class `<class '__main__.AppSettings'>` is deprecated.


A *behavior* is a way to change how a setting field behaves
during Settings object initialization and setting descriptor's
:meth:`get <concrete_settings.Setting.__get__>`
and
:meth:`set <concrete_settings.Setting.__set__>`
invocations.



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
