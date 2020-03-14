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
          SETTING_NAME: type_hint = value @behavior1 @behavior2 @...

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
      in :meth:`self.errors <Settings.errors>`.
      Otherwise a :class:`ValidationError <exceptions.ValidationError>`
      is raised when the first invalid setting is encountered.

   .. method:: validate

      Validate settings altogether.

      This is a stub method intended to be overriden when needed.
      It is called after individual settings have been validated
      without any errors.

      Raise :class:`ValidationError <exceptions.ValidationError>`
      to indicate errors.

   .. method:: errors
      :property:

      ``errors`` property contains validation errors from the last
      :meth:`settings.is_valid(raise_exception=False) <Settings.is_valid>`
      call. The errors are packed in recursive
      :class:`ValidationErrorDetail <concrete_settings.exceptions.ValidationErrorDetail>`
      structure.

   .. autoproperty:: is_being_validated

      Indicates that settings are being validated.

      The property is intended to be used by behaviors to
      distinguish between Setting reads during validation
      and normal usage.

   .. method:: update(source, [strategies])

      Update settings from the given source.

      The update process consist of two stages:

      1. Intializing an access and/or reading a source object -
         Python, YAML or JSON file, environmental variables, a dict,
         ``locals()`` etc.

      2. Stroing the read values to corresponding setting attributes.

      :param source: can either be a dict, an instance of
                     :class:`Source <concrete_settings.sources.Source>`
                     or a path to the source file.

      :param strategies: is a list of 

   .. method:: extract_to(destination, [prefix])



.. class:: concrete_settings.setting

.. class:: concrete_settings.core.PropertySetting

  ``@setting`` (an alias to ``PropertySetting`` decorator-class) is used to mark
  class methods as settings. The property-settings are read-only and used to
  compute a value, usually based on other settings. For example:

  .. testsetup:: api_property_settings

     from concrete_settings import Settings, setting

  .. testcode:: api_property_settings

     class AppSettings(Settings):
         ADMIN_NAME: str = 'Alex'
         ADMIN_EMAIL: str = 'alex@example.com'

         @setting
         def ADMIN_FULL_EMAIL(self) -> str:
             """Full admin email in `name <email>` format"""
             return f'{self.ADMIN_NAME} <{self.ADMIN_EMAIL}>'

  Note that methods written in UPPER_CASE are converted to
  ``PropertySetting`` automatically and do not require
  decoration by ``@setting``.

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
