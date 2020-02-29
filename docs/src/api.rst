.. _api:

API
===

.. module:: concrete_settings

This part of the documentation covers all the interfaces of Concrete Settings.

Settings
--------

.. autoclass:: concrete_settings.Setting

   :param typing.Any value: The default value of a setting
   :param str doc: Setting docstring
   :param tuple validators: A tuple of callable setting validators
   :param typing.Any type_hint: Setting type
   :param list behaviors: a collection of :class:`concrete_settings.Behavior` objects or 

   .. method:: __get__

   .. method:: __set__


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

.. module:: concrete_settings.behaviors

.. autoclass:: concrete_settings.Behavior



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
