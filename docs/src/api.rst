.. _api:

API
===

**======== IN PROGRESS ========**

API documentation is not complete yet.

**======== IN PROGRESS ========**

This part of the documentation briefly covers the interfaces of Concrete Settings.

Settings
--------

.. autoclass:: concrete_settings.Setting([value, *, doc, validators, type_hint, behaviors])

   A setting is a **named** object for storing, documenting and validating
   a certain value.

   :param value: the initial value of a setting with the default :class:`Undefined <concrete_settings.types.Undefined>`.
   :param doc: an end-user -friendly setting documentation.
   :param validators: setting validators, a tuple of :class:`Validator <concrete_settings.types.Validator>` callables.
   :param type_hint: setting type, something one would use as type annotation.
                     The default value
                     (:class:`GuessSettingType <concrete_settings.types.GuessSettingType>`)
                     would invoke type guessing mechanism.
   :param behaviors: setting behaviors, a container of :class:`Behavior` objects.
   :type value: :data:`Any <typing.Any>`
   :type doc: str
   :type validators: tuple
   :type type_hint: :data:`Any <typing.Any>`

   The corresponding implicit definition of a setting in Settings class is written as following:

   .. code-block::

      class MySettings(Settings):
          default_validators = (...)
          mandatory_validators = (...)

          #: Documentation is written
          #: in Sphinx-style comments above
          #: the setting definition
          SETTING_NAME: type_hint = value @ behavior1 @ behavior2 @ ...

.. autoclass:: concrete_settings.Settings

   Settings is a container for one or more :class:`Setting` objects.
   Settings classes can be mixed and nested.

   .. attribute:: default_validators

      Validators applied to each Setting that have no defined validators.

      :type: tuple[Validator]
      :value: :class:`(ValueTypeValidator(), ) <concrete_settings.validators.ValueTypeValidator>`

   .. attribute:: mandatory_validators

      Validators applied to every Setting in the class.

      :type: tuple[Validator]
      :value: ()

   .. method:: is_valid(raise_exception=False) -> bool

      Validate settings and return ``True`` if settings are valid.

      If ``raise_exception`` is False, validation errors are stored
      in ``self.errors``. Otherwise a ValidationError is raised when
      the first invalid setting is encountered.

   .. automethod:: validate

   .. autoproperty:: errors

   .. autoproperty:: is_being_validated

   .. automethod:: update

.. autoclass:: concrete_settings.core.PropertySetting

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

.. autoclass:: concrete_settings.exceptions.ValidationError


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


Exceptions
----------

.. module:: concrete_settings.exceptions

.. autodata:: ValidationErrorDetail
