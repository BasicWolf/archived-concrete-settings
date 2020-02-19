Basic concepts
##############

In this chapter we cover the essentials of Concrete Settings.

.. contents::
   :local:

Defining settings
-----------------

Defining settings starts
by subclassing the :class:`Settings <concrete_settings.Settings>`
class.
Each setting is defined by
:class:`Setting <concrete_settings.Setting>` descriptor.
The catch is that one does not have
to declare each setting explicitly.

Let's start by defining ``AppSettings``
class with a single boolean-type  ``DEBUG`` setting:

.. testcode::

   from concrete_settings import Settings, Setting
   from concrete_settings.validators import ValueTypeValidator

   class AppSettings(Settings):
       DEBUG = Setting(
           True,
           type_hint=bool,
           validators=(ValueTypeValidator(), ),
           doc="Turns debug mode on/off",
       )

And here is the short version which produces the same class as above:

.. testcode::

   from concrete_settings import Settings

   class AppSettings(Settings):

       #: Turns debug mode on/off
       DEBUG: bool = True

Though this does not truly comply with the Zen of Python

  *Explicit is better than implicit*.

wouldn't you agree that the short definition
is easier to comprehend?
The short definition looks like a boring class attribute
with a sphinx-style documentation above it.
Still, all the required details are extracted
and a corresponding ``Setting`` attribute is created.

The magic behind the scenes is happening in the metaclass
:class:`SettingsMeta <concrete_settings.core.SettingsMeta>`.
In a nutshell, if a field looks like a setting, but is not explicitly
defined as an instance of class :class:`Setting <concrete_settings.Setting>`,
a corresponding object is created instead.

:ref:`Later in the documentation <setting_declration>` the setting creation
rules are explored in-depth.
For now please accept that Concrete Settings' preferred way of declaring
*basic* settings is by omitting the ``Setting(...)`` call at all.
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


Before going further, let's take a look at the contents of a Setting object.
Each implicitly or explicitly defined setting consists of a
**name**, **default value**, a **type hint**,
**validators**, **behaviors**
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
  can use the type hint to check whether the setting value corresponds
  to the required type.
* **Validators** is a collection of callables which validate the value of the setting.
* **Behaviors** is a collection of :class:`SettingBehavior <concrete_settings.SettingBehavior>`
  objects which modify a setting's behavior during different stages of its life cycle.
* **Documentation** is a multi-line doc string intended for the end user.


Reading settings
----------------

After a Settings object has been initialized successfully it can be updated
with values from different :ref:`api_sources`, such as
:class:`YAML <concrete_settings.contrib.sources.YamlSource>` or
:class:`JSON <concrete_settings.contrib.sources.JsonSource>`
files,
:class:`enironmental variables <concrete_settings.contrib.sources.EnvVarSource>`
or a plain Python dict.

If none of the above fits your needs, check out
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

   with open('/tmp/quickstart-settings.json', 'w') as f:
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
   app_settings.update('/tmp/quickstart-settings.json')

   print(app_settings.ADMIN_EMAIL)

Output:

.. testoutput:: quickstart-json-source

   alex@my-super-app.io

.. testcleanup:: quickstart-json-source

   import os
   os.remove('/tmp/quickstart-settings.json')


.. _quickstart_validation:

Validation
----------

When Settings values have been finaly loaded, it is time
to validate each and all settings' values altogether.

A Settings object validates its setting-fields and itself when
:meth:`Settings.is_valid() <concrete_settings.Settings.is_valid()>`
is called for the first time.
Validation consists of two stages:

1. For each setting, call every :class:`validator <concrete_settings.types.Validator>`
   of ``setting.validators`` collection. This validates a setting value as standalone.

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
It is intended to be used by validators like the built-in
:class:`ValueTypeValidator <concrete_settings.validators.ValueTypeValidator>`
to validate a setting value.
Otherwise it carries no meaning and is just a valid Python object.

The :class:`ValueTypeValidator <concrete_settings.validators.ValueTypeValidator>`
is the :ref:`default validator <setting_declration_validators>`
for settings which have no validators defined explicitly:

.. testcode:: quickstart-type-hint

   from concrete_settings import Settings

   class AppSettings(Settings):
       SPEED: int = 'abc'

   app_settings = AppSettings()
   print(app_settings.is_valid())
   print(app_settings.errors)

Output:

.. testoutput:: quickstart-type-hint

   False
   {'SPEED': ["Expected value of type `<class 'int'>` got value of type `<class 'str'>`"]}


.. _quickstart_behavior:

Behavior
--------

Imagine that you would like to notify a user that a certain setting
has been deprecated.
Raising a warning when settings are initialized and
every time the setting is being read - sounds like a plan.
A straightforward way to do this is by sublassing the
:class:`Setting <concrete_settings.Setting>` class and overriding
:meth:`Setting.__get__() <concrete_settings.Setting.__get__>`.

Another way would be using the supplied Settings Behavior mechanism.
Behaviors can be passed to a Setting explicitly.
But the preferred way is to use the syntactic sugar - by "decorating" settings.
For example, let's take a look at the built-in :class:`deprecated <concrete_settings.contrib.behaviors.deprecated>`
behavior. It simply adds :class:`DeprecatedValidator <concrete_settings.contrib.validators.DeprecatedValidator>`
to the setting. The rationale of using the behavior instead of a validator is improved readability.
Just have a look:

.. testcode:: quickstart-behavior

   from concrete_settings import Settings, Setting
   from concrete_settings.contrib.behaviors import deprecated

   class AppSettings(Settings):
       MAX_SPEED: int = 30 @deprecated

   app_settings = AppSettings()
   app_settings.is_valid()

The explicit equivalent definition is:

.. testcode:: quickstart-behavior

   class AppSettings(Settings):
       MAX_SPEED: int = Setting(30, behaviors=(deprecated, ))

If Python warnings are enabled (e.g. ``python -Wdefault``), you would
get a warning in stderr:


.. code-block:: none

   DeprecationWarning: Setting `MAX_SPEED` in class `<class '__main__.AppSettings'>` is deprecated.

In a nutshell, a *behavior* is a way to change how a setting field behaves
during its initialization, validation and setting's
:meth:`get <concrete_settings.Setting.__get__>`
and
:meth:`set <concrete_settings.Setting.__set__>`
descriptors invocations.
A behavior can be passed to :class:`Setting.__init__() <concrete_settings.Setting>`
or by using ``@`` operator: ``value @ behavior0 @ behavior1 @ ...``



Nested settings
---------------

Nesting is a nice and simple way to logically group and isolate settings.
Let's try grouping *database*, *cache* and *logging* in
application settings as follows:

.. testcode:: quickstart-nested

   from concrete_settings import Settings

   class DBSettings(Settings):
       USER = 'alex'
       PASSWORD  = 'secret'
       SERVER = 'localhost@5432'

   class CacheSettings(Settings):
       ENGINE = 'DatabaseCache'
       TIMEOUT = 300

   class LoggingSettings(Settings):
       LEVEL = 'INFO'
       FORMAT = '%(asctime)s %(levelname)-8s %(name)-15s %(message)s'


   class AppSettings(Settings):
       DB = DBSettings()
       CACHE = CacheSettings()
       LOG = LoggingSettings()

   app_settings = AppSettings()
   print(app_settings.LOG.LEVEL)

Output:

.. testoutput:: quickstart-nested

   INFO

At first glance, there is nothing special about this code.
What makes it special and somewhat confusing is
that class :class:`Settings <concrete_settings.Settings>` is a
subclass of class :class:`Setting <concrete_settings.Setting>`!
Hence, nested Settings behave and can be treated
as Setting descriptors - e.g. have validators, documentation
or bound behavior.

Additionally, validating top-level settings
automatically cascades to all nested settings.
The following example ends up with a validation error:


.. testcode:: quickstart-nested2

   from concrete_settings import Settings

   class DBSettings(Settings):
       USER: str = 123
       ...

   class AppSettings(Settings):
       DB = DBSettings()
       ...

   app_settings = AppSettings()
   app_settings.is_valid(raise_exception=True)

.. testoutput:: quickstart-nested2

   Traceback (most recent call last):
       ...
   concrete_settings.exceptions.SettingsValidationError: DB: Expected value of type `<class 'str'>` got value of type `<class 'int'>`


Combining settings
------------------

Another way of putting settings together is by using Python's
multi-inheritance mechanism.
It it very useful when putting a framework and application
settings together. For example, Django settings and
application settings can be separated as follows:

.. testcode:: quickstart-combined-framework

   from concrete_settings import Settings
   from concrete_settings.contrib.frameworks.django30 import Django30Settings

   class ApplicationSettings(Settings):
       GREETING = 'Hello world!'

   class SiteSettings(ApplicationSettings, Django30Settings):
       pass

   site_settings = SiteSettings()
   print(site_settings.GREETING)
   print(site_settings.EMAIL_BACKEND)

Output:

.. testoutput:: quickstart-combined-framework

   Hello world!
   django.core.mail.backends.smtp.EmailBackend

Another use case is extracting settings to own classes
and combining them to mimic legacy settings module interface.
For example, let's combine Database and Log settings:

.. testcode:: quickstart-combined

   from concrete_settings import Settings, prefix

   @prefix('DB')
   class DBSettings(Settings):
       USER = 'alex'
       PASSWORD  = 'secret'
       SERVER = 'localhost@5432'

   @prefix('LOG')
   class LoggingSettings(Settings):
       LEVEL = 'INFO'
       FORMAT = '%(asctime)s %(levelname)-8s %(name)-15s %(message)s'

   class AppSettings(
       DBSettings,
       LoggingSettings
   ):
       pass

   app_settings = AppSettings()
   print(app_settings.LOG_LEVEL)
   print(app_settings.DB_USER)

.. testoutput:: quickstart-combined
   :hide:

   INFO
   alex

The :class:`prefix <concrete_settings.prefix>` decorator is used to add
a common prefix to all setting-fields of the decorated Settings class.

Note that Python rules of multiple inheritance are applied.
For example :meth:`validate() <concrete_settings.Settings.validate>`
must be explicitly called for each of the base classes:

.. testcode:: quickstart-combined

   class AppSettings(
       DBSettings,
       LoggingSettings
   ):
       def validate(self):
           super().validate()
           DBSettings.validate(self)
           LoggingSettings.validate(self)



What's next?
------------

Now that you know the basics, why not to try adding
Concrete Settings to your application?
A minimal user-friendly setup is shown in :ref:`startup` section.
