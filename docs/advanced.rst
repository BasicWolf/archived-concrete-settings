Advanced topics
===============

In this chapter we explore the ConcreteSettings in-depth.

.. contents::
   :local:

.. testsetup::

   from concrete_settings import Settings

.. _automated_setting:

Automated Setting creation
--------------------------

Quickstart introduced the concept of automated setting creation.
Recall, that a setting object is created out of an implicit
definition, such as:

.. testcode::

   from concrete_settings import Settings

   class AppSettings(Settings):

       #: Turns debug mode on/off
       DEBUG: bool = True

In this section we discuss this process, i.e. how
``DEBUG`` from the example above turns into
:class:`Setting <concrete_settings.Setting>`
descriptor instance.

ConcreteSettings has to find
a setting attribute :ref:`name <automated_setting_name>`,
:ref:`default value <automated_setting_default_value>`
and :ref:`type hint <automated_setting_type_hint>`,
its :ref:`validators <automated_setting_validators>`,
:ref:`behaviors <automated_setting_behaviors>`
and :ref:`documentation <automated_setting_documentation>`


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

.. _automated_setting_name:

Name
....

**TODO**: @setting

Every attribute with **name** written in upper case
is considered a potential Setting.
The exceptions are attributes starting with underscore:

.. testcode::

   class AppSettings(Settings):
       debug = True   # not a setting
       _DEBUG = True  # not a setting
       DEBUG = True   ### considered a setting


.. _automated_setting_default_value:

Default value
.............

**TODO**: @setting

The *default value* is the value assigned to the attribute:

.. testcode::

   class AppSettings(Settings):
       DEBUG = True  # default value is `True`
       MAX_SPEED = 10  # default value is `10`

When default value is not available (e.g. database credentials),
use the special :class:`Undefined <concrete_settings.types.Undefined>`
value:

.. testcode::

   from concrete_settings import Undefined

   class DBSettings(Settings):
       USERNAME: str = Undefined
       PASSWORD: str = Undefined

``Undefined`` implies that the setting value would be set later in runtime
*before validation*.
:class:`RequiredValidator <concrete_settings.validators.RequiredValidator>`
would fail validation if the setting's value is ``Undefined``.

.. _automated_setting_type_hint:

Type hint
.........

**TODO**: @setting

A type hint is defined by a standard Python type annotation:

.. testcode::

   class AppSettings(Settings):
       MAX_SPEED: int = 10  # type hint is `int`

If an attribute is not type-annotated, a *type hint* is computed
by calling :class:`type() <type>` on the default value. The recognized types
are declared in
:attr:`GuessSettingType.KNOWN_TYPES <concrete_settings.types.GuessSettingType.KNOWN_TYPES>`.
If the type is not recognized, the type hint is set to :data:`typing.Any`.

.. testcode::

   class AppSettings(Settings):
       DEBUG = True  # default value `True`, type `bool`
       MAX_SPEED = 300   # default value `300`, type `int`

**It is recommended to explicitly annotate a setting with the intended type,
in order to avoid invalid type detections**:

.. testcode::

   class AppSettings(Settings):
       DEBUG: bool = True      # default value `True`, type `bool`
       MAX_SPEED: int  = 300   # default value `300`, type `int`

Type annotation is intended for validators, such as
:class:`ValueTypeValidator <concrete_settings.validators.ValueTypeValidator>`.
It fails validation if the type of the setting's
value does not correspond to the type hint.

.. _automated_setting_validators:

Validators
..........

**TODO**: @setting

Validators is a collection of callables which validate the value of the setting.
The interface of the callable is defined in :meth:`Validator.__call__() <concrete_settings.validators.Validator.__call__>`.
If validation fails, a validator raises
:class:`SettingsValidationError <concrete_settings.exceptions.SettingsValidationError>`
with failure details.
Individual Setting validators are supplied in ``validators`` argument of an explicit Setting declaration.
Also some :ref:`behaviors <automated_setting_behaviors>` add certain validators to a setting.

The *mandatory validators* are applied to every Setting in Settings.
They are defined
in :attr:`Settings.mandatory_validators <concrete_settings.Settings.mandatory_validators>` tuple.
The *default validators* are applied to a Setting that has no validators of its own.
They are defined in
:attr:`Settings.default_validators <concrete_settings.Settings.default_validators>`.
:class:`ValueTypeValidator <concrete_settings.validators.ValueTypeValidator>` is
the only validator in the base ``Settings.default_validators``.

.. testsetup::

   from concrete_settings.validators import ValueTypeValidator

   assert len(Settings.default_validators) == 1, 'Default validators is expected to have a single validator'
   assert isinstance(Settings.default_validators[0], ValueTypeValidator)

Note, that both lists are inherited by standard Python class inheritance rules.
For example, to extend ``default_validators`` in a derived class, use
concatenation. In the following example
:class:`RequiredValidator <concrete_settings.validators.RequiredValidator>`
is added to ``default_validators`` to prevent any
:class:`Undefined <concrete_settings.types.Undefined>` values appearing
in the validated settings:

.. testcode:: advanced-default-validators-undefined

   from concrete_settings import Settings, Undefined
   from concrete_settings.validators import RequiredValidator

   class AppSettings(Settings):
       default_validators = Settings.default_validators + (RequiredValidator(), )

       ADMIN_NAME: str = Undefined

   app_settings = AppSettings()
   print(app_settings.is_valid())
   print(app_settings.errors)

Output:

.. testoutput:: advanced-default-validators-undefined

   False
   {'ADMIN_NAME': ['Setting `ADMIN_NAME` is required to have a value. Current value is `Undefined`']}


.. _automated_setting_behaviors:

Behaviors
.........

*Setting Behaviors* allow executing some logic on different stages of a Setting lifecycle.
one has to bind a
:class:`SettingBehavior <concrete_settings.behaviors.SettingBehavior>` to it.

In addition to declaring behaviors in a Setting
:class:`constructor <concrete_settings.Setting>`,
ConcreteSettings utilizes matrix multiplication ``@`` (:meth:`object.__rmatmul__`) to
add a behavior to a Setting. Let's declare the ``ADMIN_NAME`` setting from the
example above as :class:`required <concrete_settings.contrib.behaviors.required>`:

.. testcode::

   from concrete_settings import Settings, Undefined
   from concrete_settings.contrib.behaviors import required

   class AppSettings(Settings):
       ADMIN_NAME: str = Undefined @required

The equivalent explicit form is:

.. testcode::

   from concrete_settings import Setting, Settings, Undefined
   from concrete_settings.contrib.behaviors import required

   class AppSettings(Settings):
       ADMIN_NAME: str = Setting(Undefined, behaviors=(required, ))

Behaviors can also decorate the property-setting getters:

.. testcode::

   from concrete_settings import Settings, Undefined, setting
   from concrete_settings.contrib.behaviors import required

   class AppSettings(Settings):
       @required
       @setting
       def ADMIN_NAME(self) -> str:
           return Undefined

Validating any of the previous examples as

.. testcode::

   app_settings = AppSettings()
   print(app_settings.is_valid())
   print(app_settings.errors)

yields the following output:

.. testoutput::

   False
   {'ADMIN_NAME': ['Setting `ADMIN_NAME` is required to have a value. Current value is `Undefined`']}


.. _automated_setting_documentation:

Documentation
.............

**TODO**: @setting

Update strategies
-----------------

In most cases, a developer wants to overwrite a setting value
when updating it from a source. But there are exceptions.
Think of a list setting, which contains administrators' emails, e.g.:

.. testcode:: quickstart-update-strategies

   from typing import List
   from concrete_settings import Settings

   class AppSettings(Settings):
       ADMIN_EMAILS: List[str] = [
           'admin@example.com'
       ]


What if you want to **append** the emails defined in sources, instead
of overwriting them? ConcreteSettings provides a concept of
:mod:`update strategies <concrete_settings.sources.strategies>`
for such cases:

.. code-block:: json

   {
       "ADMIN_EMAILS": ["alex@my-super-app.io"]
   }

.. testsetup:: quickstart-update-strategies

   with open('/tmp/cs-quickstart-settings.json', 'w') as f:
       f.write('''
           {
               "ADMIN_EMAILS": ["alex@my-super-app.io"]
           }
       ''')

.. testcode:: quickstart-update-strategies

   from concrete_settings.sources import strategies

   ...

   app_settings = AppSettings()
   app_settings.update('/tmp/cs-quickstart-settings.json', strategies={
       'ADMIN_EMAILS': strategies.append
   })
   print(app_settings.ADMIN_EMAILS)

.. testcleanup:: quickstart-update-strategies

   import os
   os.remove('/tmp/cs-quickstart-settings.json')

Output:

.. testoutput:: quickstart-update-strategies

   ['admin@example.com', 'alex@my-super-app.io']


.. _advanced_validators:

Validators
----------
