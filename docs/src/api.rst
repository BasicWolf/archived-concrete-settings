.. _api:

API
===

This part of the documentation briefly covers the interfaces of Concrete Settings.

Settings
--------

.. module:: concrete_settings.setting

.. autoclass:: Setting

   A setting is a **named** object for storing, documenting and validating
   a certain value.

   :param value: the initial value of a setting with the default
                 :class:`Undefined <concrete_settings.types.Undefined>`.
   :param doc: an end-user -friendly setting documentation.
   :param validators: setting validators, a tuple of
                      :class:`Validator <concrete_settings.validators.Validator>` callables.
   :param type_hint: setting type, something one would use as type annotation.
                     The default value
                     (:class:`GuessSettingType <concrete_settings.types.GuessSettingType>`)
                     would invoke type guessing mechanism.
   :param override: a indicates that settings definiton is explicitly overriden.
   :type value: :data:`Any <typing.Any>`
   :type doc: str
   :type validators: tuple
   :type type_hint: :data:`Any <typing.Any>`
   :type override: bool

   The corresponding implicit definition of a setting in Settings class is written as following:

   .. code-block::

      class MySettings(Settings):
          default_validators = (...)
          mandatory_validators = (...)

          #: Documentation is written
          #: in Sphinx-style comments above
          #: the setting definition
          SETTING_NAME: type_hint = value @behavior1 @behavior2 @...

   .. attribute:: name

      Setting attribute name (read-only).

   .. attribute:: _behaviors

      Internal attribute for storing behaviors attached to the setting

.. module:: concrete_settings.settings

.. autoclass:: Settings

   Settings is a container for one or more :class:`Setting <concrete_settings.setting.Setting>` objects.
   Settings classes can be mixed and nested.

   .. attribute:: default_validators

      Validators applied to each Setting that have no defined validators.

      :type: tuple[Validator]
      :value: ()

   .. attribute:: mandatory_validators

      Validators applied to every Setting in the class.

      :type: tuple[Validator]
      :value: :class:`(ValueTypeValidator(), ) <concrete_settings.validators.ValueTypeValidator>`

   .. method:: is_valid(raise_exception=False) -> bool

      Validate settings and return ``True`` if settings are valid.

      If ``raise_exception`` is False, validation errors are stored
      in :meth:`self.errors <Settings.errors>`.
      Otherwise a :class:`ValidationError <concrete_settings.exceptions.ValidationError>`
      is raised when the first invalid setting is encountered.

   .. method:: validate

      Validate settings altogether.

      This is a stub method intended to be overriden when needed.
      It is called after individual settings have been validated
      without any errors.

      Raise :class:`ValidationError <concrete_settings.exceptions.ValidationError>`
      to indicate errors.

   .. method:: errors
      :property:

      ``errors`` property contains validation errors from the last
      :meth:`settings.is_valid(raise_exception=False) <Settings.is_valid>`
      call. The errors are packed in recursive
      :class:`ValidationErrorDetail <concrete_settings.exceptions.ValidationErrorDetails>`
      structure.

   .. method:: is_being_validated
      :property:

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

      2. Update the settings by the values read from the sources.

      :param source: can either be a :class:`dict`, an instance of
                     :class:`Source <concrete_settings.sources.Source>`
                     or a path to the source file.

      :param strategies: a dictionary of
                         { setting_name:
                         :class:`Strategy <concrete_settings.sources.strategies.Strategy>`}
                         which affect how settings' values are updated.


   .. method:: extract_to(destination, [prefix])



.. class:: setting

.. class:: PropertySetting

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

Types
-----

.. module:: concrete_settings.types

.. autoclass:: Undefined

  A special Setting value which indicates
  that a value should be set by other means, e.g. by updating
  the settings object.
  Often used in conjuction with
  :class:`RequiredValidator <concrete_settings.validators.RequiredValidator>`
  and
  :class:`required <concrete_settings.contrib.behaviors.required>` behavior.

  .. testsetup:: api_prefix

     from concrete_settings import Settings, Undefined

  .. testcode:: api_prefix

     class AppSettings(Settings):
        SPEED: int = Undefined


.. autoclass:: GuessSettingType

   A special value for ``Setting.type_hint``, which indicates
   that a Setting type should be guessed from the default value.

   For an ``Undefined`` or an unknown type, the guessed type
   hint is :class:`typing.Any`.

   .. autoattribute:: KNOWN_TYPES


Validators
----------

.. module:: concrete_settings.validators

.. autoclass:: Validator(Protocol)
   :members: __call__

.. module:: concrete_settings.exceptions

.. autoclass:: ValidationError(details: :data:`ValidationErrorDetails`)

   Raised by a setting validator when a setting value is invalid.

.. autodata:: ValidationErrorDetails

   A recursive union type which describes validation errors.

   ``ValidationErrorDetails`` is defined as

   ::

      SettingName = str

      ValidationErrorDetails = Union[
          str,
          List[ValidationErrorDetails],
          Dict[SettingName, ValidationErrorDetails]
      ]



ValueTypeValidator
..................

.. autoclass:: concrete_settings.validators.ValueTypeValidator

   Matches setting value type and its type hint.

   Setting value type should match ``setting.type_hint``.
   :class:`Undefined <concrete_settings.types.Undefined>` value is considered
   valid for any type hint.

   ``ValueTypeValidator`` is the default validator in
   :data:`Settings.mandatory_validators <concrete_settings.settings.Settings.mandatory_validators>`.

   :param type_hint: If ``setting.type_hint`` is ``None``, then
                     type match is performed against the given
                     ``type_hint``.


RequiredValidator
.................

.. autoclass:: concrete_settings.validators.RequiredValidator

   Validates that setting value is not
   :class:`Undefined <concrete_settings.types.Undefined>`
   For convenient usage, see
   :class:`required <concrete_settings.contrib.behaviors.required>`
   behavior.

   :param message: Custom validation error message template.

   :value message: "Setting `{name}` is required to have a value.
                    Current value is \`Undefined\`"


.. testcode::
   :hide:

   from concrete_settings.validators.required_validator import RequiredValidator
   assert RequiredValidator().message == (
       'Setting `{name}` is required to have a value. '
       'Current value is `Undefined`'
   )


DeprecatedValidator
...................

.. autoclass:: concrete_settings.contrib.validators.DeprecatedValidator

   Emits a warning or raises
   `ValidationError <concrete_settings.exceptions.ValidationError>`
   indicating that setting is deprecated.

   This is a helper validator added to a Setting attribute validators
   by :class:`@deprecated <concrete_settings.contrib.behaviors.deprecated>`
   behavior.

Behaviors
---------

.. module:: concrete_settings.behaviors

.. autoclass:: Behavior

   Base class for Setting attributes behaviors.

   .. method:: decorate(setting: concrete_settings.setting.Setting)

      Decorate setting attribute.

      If your custom behavior adds a validator to the Setting,
      override this method as follows:

      .. code-block::

         def decorate(self, setting):
            setting.validators = (
                MyValidator()
            ) + setting.validators

            super().attach_to(setting)

      :param setting: Setting to which the behavior is attached.
      :return: Passed setting object.


.. autoclass:: GetterSetterBehavior

   A base class for behaviors which provide custom get / set behavior.
   The super class methods have to be invoked to invoke behaviors get / set
   chain down to the decorated original setting.

   .. automethod:: get_value

      :param Setting setting: Setting to which behavior is attached.
      :param Settings owner: Settings object - setting attribute's owner.

      Invoked when the decorated Setting is being read.


      When overriding this method remember to call the base class method
      ``super().get_value(setting, owner)`` to invoke the chained behaviors down
      to the setting's original value getter. For example:

      .. code-block::

         def get_value(self, setting: 'Setting', owner: 'Settings') -> Any:
             val =  super().get_value(setting, owner)
             print(f"Setting {setting.name} has been accessed, its value was {val}")
             return val


   .. automethod:: set_value

      :param Setting setting: Setting to which behavior is attached.
      :param Settings owner: Settings object - setting attribute's owner.
      :param value: Value being written to the setting.

      Invoked when the decorated Setting is being written.

      When overriding this method, remember to call the base class method
      ``super().set_value(setting, owner, value)`` to invoke the chained
      behaviors down to the setting's original value setter.

override
........

.. autoclass:: override

Sets ``Setting.override = True``.

Usage:

.. testcode:: api_override_behavior

   from concrete_settings import Settings, override

   class BaseSettings(Settings):
       SECRET: int = 100200300400500
       ...

   class DevSettings(BaseSettings):
       SECRET: str = 'abcdef12345' @override

validate
........

.. autoclass:: concrete_settings.validate

Provides behavior-style way of attaching validators to a setting.

.. testcode:: api_validate_behavior

   from concrete_settings import Settings, validate, ValidationError

   def is_positive(value, **kwargs):
       if value <= 0:
           raise ValidationError(f'must be a positive integer')

   class AppSettings(Settings):
       SPEED: int = 20 @ validate(is_positive)

   app_settings = AppSettings()
   app_settings.SPEED = -10

   print(app_settings.is_valid())
   print(app_settings.errors)

.. testoutput:: api_validate_behavior

   False
   {'SPEED': ['must be a positive integer']}

required
........

.. autoclass:: concrete_settings.contrib.behaviors.required

   Attaches
   :class:`RequiredValidator <concrete_settings.validators.RequiredValidator>`
   to the setting which
   validates that setting value is not
   :class:`Undefined <concrete_settings.types.Undefined>`.

   Usage:

   .. testcode:: api_required_behavior

      from concrete_settings import Settings, Undefined, required

      class AppSettings(Settings):
          SECRET_STRING: str = Undefined @required


deprecated
..........

.. autoclass:: concrete_settings.contrib.behaviors.deprecated

   Emit warnings when Setting is read, written or being validated.

   :param deprecation_message: Warning message template. Placeholders:

                               * ``{name}`` - setting name.
                               * ``{owner}`` - owner :class:`Settings <concrete_settings.settings.Settings>` object.

   :param bool warn_on_validation: Add warning-raising
                                   :class:`DeprecatedValidator <concrete_settings.contrib.validators.DeprecatedValidator>`
                                   to the setting's validators list.
   :param bool error_on_validation: Add exception-raising
                                    :class:`DeprecatedValidator <concrete_settings.contrib.validators.DeprecatedValidator>`
                                    to the setting's validators list. When this parameter is set to ``True``,
                                    ``warn_on_validation`` is ignored.

   :param bool warn_on_get: Emit warning when reading the setting.
   :param bool warn_on_set: Emit warning when writing the setting.


.. _api_sources:

Sources
-------

.. module:: concrete_settings.sources

.. data:: AnySource

   ``AnySource = Union[Dict[str, Any], str, 'Source', Path]``

   Valid settings sources types union.
   A valid source is either a ``dict``, an instance of
   :class:`Source <concrete_settings.sources.Source>` or
   a path (str or :class:`Path <pathlib.Path>`)

.. autoclass:: Source

   The base class of all Concrete Settings sources.

   .. automethod:: get_source

      :param src: some source representation
      :type src: :data:`AnySource`

      A **static** method which returns a ``Source`` instance
      or ``None`` if ``src`` is not suitable.
      For example, :class:`DictSource <concrete_settings.sources.DictSource>`
      implements it as follows:

   .. code-block::

     @staticmethod
     def get_source(src: AnySource) -> Optional['DictSource']:
         if isinstance(src, dict):
             return DictSource(src)
         elif isinstance(src, DictSource):
             return src
         else:
             return None

   .. automethod:: read

      :param setting: Setting attribute instance being processed.
                      Usually :data:`setting.name <concrete_settings.setting.Setting.name>` is of interest.
      :param parents: A chain of parent Settings classes names (i.e. in case of nested
                      settings). This is used to map *source* setting keys like
                      ``DB_HOST_PORT`` to ``AppSettings.DB.HOST.PORT``.
                      In this case ``parents=('DB', 'HOST')``.
      :type setting: :class:`Setting <concrete_settings.setting.Setting>`
      :type parents: tuple[str]

      Called for each setting from settings beign read. A source should
      return the corresponding value.

      ``read()`` should return :class:`NotFound` if setting value was not provided by the source.

.. autoclass:: NotFound

   Returned by :meth:`Source.read <Source.read>` when setting value is not provided by the source.

.. autoclass:: DictSource

   Python :class:`dict` -parsing source.


Update strategies
.................

.. module:: concrete_settings.sources.strategies

.. autoclass:: Strategy(Protocol)

   A strategy decides how a setting value will be :meth:`updated <concrete_settings.settings.Settings.update>`.

   .. automethod:: __call__(current_value, new_value)

      The signature of Strategy callables

      :param current_value: is the current value of a setting
      :param new_value: is the new_value from a source.

   Usually a strategy is a simple and small function.
   For example if a setting is a tuple, the following strategy
   would append values, instead of overwriting the tuple:

   .. testsetup:: api_strategies

     from typing import Tuple
     from concrete_settings import Settings

   .. testcode:: api_strategies

      # the required strategy
      def append(new_val, old_val):
          return new_val + old_val

      class AppSettings(Settings):
          ADMIN_EMAILS: Tuple[str] = ('cto@example.com', )

      app_settings = AppSettings()
      app_settings.update(
          source={
              'ADMIN_EMAILS': ('alex@example.com', )
          },
          strategies={
              'ADMIN_EMAILS': append
          }
      )

      print(app_settings.ADMIN_EMAILS)

   Output:

   .. testoutput:: api_strategies

      ('cto@example.com', 'alex@example.com')
