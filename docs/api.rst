.. _api:

API
===

.. module:: concrete_settings

This part of the documentation covers all the interfaces of Concrete Settings.

Settings
--------

.. autoclass:: concrete_settings.Setting
   :members:
   :special-members: __get__,__set__

.. autoclass:: concrete_settings.Settings
   :members:

.. autoclass:: concrete_settings.PropertySetting
   :members:

.. autoclass:: concrete_settings.prefix

.. autoclass:: concrete_settings.core.SettingsMeta

Types
-----

.. module:: concrete_settings.types

.. autoclass:: Undefined

.. autoclass:: GuessSettingType

   .. autoattribute:: KNOWN_TYPES


Validators
----------

.. module:: concrete_settings.validators

.. autoclass:: Validator
   :members: __call__

.. autoclass:: concrete_settings.exceptions.SettingsValidationError

ValueTypeValidator
..................

.. autoclass:: ValueTypeValidator


RequiredValidator
.................

.. autoclass:: RequiredValidator


DeprecatedValidator
...................

.. autoclass:: concrete_settings.contrib.validators.DeprecatedValidator


Behaviors
---------

.. module:: concrete_settings.behaviors

.. autoclass:: concrete_settings.behaviors.SettingBehavior



deprecated
..........

.. autoclass:: concrete_settings.contrib.behaviors.deprecated


.. _api_sources:

Sources
-------

.. module:: concrete_settings.sources

.. autoclass:: concrete_settings.sources.Source

Update strategies
.................

.. module:: concrete_settings.sources.strategies



Built-in Sources
................

.. autoclass:: concrete_settings.contrib.sources.YamlSource

.. autoclass:: concrete_settings.contrib.sources.JsonSource

.. autoclass:: concrete_settings.contrib.sources.EnvVarSource
