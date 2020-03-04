.. _api:

API
===

This part of the documentation briefly covers the interfaces of Concrete Settings.

Settings
--------

.. autoclass:: concrete_settings.Setting

   A setting is a named object for storing, documenting and validating
   a certain value.

   :param value: the initial value of a setting with the default :class:`Undefined <concrete_settings.types.Undefined>`.
   :param doc: an end-user -friendly setting documentation.
   :param validators: setting validators, a tuple of :class:`Validator <concrete_settings.types.Validator>` callables.
   :param type_hint: setting type, something one would use as type annotation.
   :param behaviors: setting behaviors, a container of :class:`Behavior` objects.


.. autoclass:: concrete_settings.Settings
   :members:

   Settings is a container for one or more :class:`Setting` objects.
   Settings classes can be mixed and nested.

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
