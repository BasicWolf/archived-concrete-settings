Advanced topics
===============

In this chapter we discover Concrete Settings in-depth

.. contents::
   :local:


Nested Settings
---------------

Nesting is a great way to logically group and isolate settings.
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
or :ref:`bound behavior <quickstart_behavior>`.

Additionally, :ref:`validating <quickstart_validation>` top-level settings
automatically cascades to all nested settings.



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
