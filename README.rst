Welcome
#######

**concrete-settings** is a small library which helps handling settings in large projects.

It is built on the following concepts:

* Settings are declared in classes.
* Settings should be documented and there should be a way to easily fetch documentation.
* Settings should be type-annotated and validated.
* Settings should be mixable and nestable.


.. code-block::

   class CommonSettings(Settings):
       # This is the documentation of MAX_SPEED setting
       MAX_SPEED: int = 100
