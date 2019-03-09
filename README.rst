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
       # This is the documentation of MAX_SPEED setting
       MAX_SPEED: int = 100

Overriding settings
-------------------

.. code-block:: python

    class S(ConcreteSettings):
        T: int = 10


    class S2(S):
        T: str = OverrideSetting('hello')

    >>> S1().T == 'hello'
