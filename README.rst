Welcome
#######

**concrete-settings** is a small library which helps handling settings in large projects.

It is built on the following concepts:

* Settings are declared in classes.
* Settings should be documented and there should be a way to easily fetch documentation.
* Settings should be type-annotated and validated.
* Settings should be mixable and nestable.


.. code-block:: python

   class CommonSettings(Settings):
       #: This is the documentation of MAX_SPEED setting
       MAX_SPEED: int = 100

Overriding settings
-------------------

.. code-block:: python

    class S(ConcreteSettings):
        SPEED: int = 10

    # Protect from accidental type changes
    class S1(S):
        SPEED: str = 'hello'

.. code-block:: pycon

    >>> S2(); S2.is_valid(raise_exception=True)
    SettingsValidationError:
        SPEED:
            in classes <class 'S'> and <class 'S1'> setting has the following difference(s):
            types differ: <class 'int'> != <class 'str'>

.. code-block:: python

    # Override is required
    class S2(S):
        SPEED: str = OverrideSetting('hello')

.. code-block:: pycon

    >>> S2();
    >>> S2.is_valid()
        True


Deprecated settings
-------------------

.. code-block:: python

  class S0(Settings):
      SPEED: int = DeprecatedSetting(10)


  >>> S0()
  DepracationWarning: SPEED in class 'S0': Setting is deprecated and will be removed in future
