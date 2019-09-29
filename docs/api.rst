.. _api:

API
===

.. module:: concrete_settings

This part of the documentation covers all the interfaces of Concrete Settings.

Settings
--------

.. autoclass:: concrete_settings.Setting
   :members:

.. autoclass:: concrete_settings.Settings
   :members:

.. autoclass:: concrete_settings.PropertySetting
   :members:

.. autoclass:: concrete_settings.concrete_settings.SettingsMeta


Types
-----

.. module:: concrete_settings.types

.. autoclass:: concrete_settings.types.Undefined

.. autoclass:: concrete_settings.types.GuessSettingType

   .. autoattribute:: KNOWN_TYPES

Validators
----------

.. module:: concrete_settings.validators

.. autoclass:: concrete_settings.validators.Validator
   :members: __call__

.. autoclass:: concrete_settings.validators.ValueTypeValidator


.. _api_sources:

Sources
-------

.. module:: concrete_settings.sources

.. autoclass:: concrete_settings.sources.Source

.. autoclass:: concrete_settings.sources.YamlSource

.. autoclass:: concrete_settings.sources.JsonSource

.. autoclass:: concrete_settings.sources.EnvVarSource
