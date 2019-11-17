Advanced topics
===============

In this chapter we explore the Concrete Settings in-depth.

.. contents::
   :local:

.. _automated_setting:

Automated Setting creation
--------------------------

Quickstart introduced the concept of automated setting creation.
Recall, that a setting object is created out of an implicit
definition, such as

.. testcode::

   from concrete_settings import Settings

   class AppSettings(Settings):

       #: Turns debug mode on/off
       DEBUG: bool = True

In this section we discuss this process, i.e. how
``DEBUG`` from the example above turns into
:class:`Setting <concrete_settings.Setting>`
descriptor instance.

The challenge of converting the implicit definition
to an explicit one, is to figure out the
setting attribute :ref:`name <automated_setting_name>`,
its :ref:`default value <automated_setting_default_value>`,


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

.. code-block::

   class AppSettings(Settings):

       debug = True   # not considered a setting

       _DEBUG = True  # not considered a setting

       DEBUG = True   # considered a setting

.. _automated_setting_default_value:

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

.. _automated_setting_type_hint:

**Type hint**

.. _automated_setting_validators:

**Validators**

.. _automated_setting_behaviors:

**Behaviors**


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
