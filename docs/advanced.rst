Advanced topics
===============

In this chapter we explore the Concrete Settings in-depth.

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

Concrete Settings has to find
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

**Name**

Every attribute with **name** written in upper case
is considered a potential Setting.
The exceptions are attributes starting with underscore:

.. testcode::

   class AppSettings(Settings):
       debug = True   # not a setting
       _DEBUG = True  # not a setting
       DEBUG = True   ### considered a setting

.. _automated_setting_default_value:

**Default value**

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

**Type hint**

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

**Validators**

Validators is a collection of callables which validate the value of the setting.
The interface of the callable is defined in :meth:`Validator.__call__ <concrete_settings.validators.Validator.__call__>`.

If validation fails, a validator should raise :class:`SettingsValidationError <concrete_settings.exceptions.SettingsValidationError>` with failure details.

.. _automated_setting_behaviors:

**Behaviors**

.. _automated_setting_documentation:

**Documentation**

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
of overwriting them? Concrete Settings provides a concept of
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
