.. _api:

API
===

This part of the documentation covers all the interfaces of Concrete Settings.

Settings
--------

.. autoclass:: concrete_settings.Setting

   A setting is a named object for storing, documenting and validating
   a certain value.

   :param value: the initial value of a setting. If no value is given,
   :param doc: a user-friendly setting documentation.
   :param validators: setting validators.
   :param type_hint: setting type.
   :param behaviors: setting behaviors.


.. autoclass:: concrete_settings.Settings
   :members:

   .. attribute:: default_validators

   .. attribute:: mandatory_validators

.. autoclass:: concrete_settings.core.PropertySetting
   :members:

.. autoclass:: concrete_settings.setting

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

.. autoclass:: Validator
   :members: __call__

.. autoclass:: concrete_settings.exceptions.SettingsValidationError


.. module:: concrete_settings.validators

ValueTypeValidator
..................

.. autoclass:: concrete_settings.validators.ValueTypeValidator


RequiredValidator
.................

.. autoclass:: concrete_settings.validators.RequiredValidator


DeprecatedValidator
...................

.. autoclass:: concrete_settings.contrib.validators.DeprecatedValidator


Behaviors
---------

.. autoclass:: concrete_settings.Behavior

.. autoclass:: concrete_settings.Behaviors


deprecated
..........

.. autoclass:: concrete_settings.contrib.behaviors.deprecated


required
........

.. autoclass:: concrete_settings.contrib.behaviors.required

.. _api_sources:


Sources
-------

.. module:: concrete_settings.sources

.. autoclass:: concrete_settings.sources.Source


Built-in Sources
................

.. autoclass:: concrete_settings.contrib.sources.YamlSource

.. autoclass:: concrete_settings.contrib.sources.JsonSource

.. autoclass:: concrete_settings.contrib.sources.EnvVarSource

Update strategies
.................

.. module:: concrete_settings.sources.strategies
