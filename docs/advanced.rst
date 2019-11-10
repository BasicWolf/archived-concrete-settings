Advanced topics
===============

In this chapter we discover Concrete Settings in-depth

.. contents::
   :local:


Update strategies
-----------------

In most of the cases, a developer wants to overwrite a setting value
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
