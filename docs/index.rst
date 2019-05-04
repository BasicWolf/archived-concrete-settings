.. Concrete Settings documentation master file, created by
   sphinx-quickstart on Sun Apr 14 18:28:20 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Concrete Settings
============================

**Concrete Settings** is a small Python library which helps handling configuration in large projects.

**WARNING!** Concrete Settings is currently in development! There is no stable, not even pre-alpha version currently available.

What are the goals of this library?

1. Provide a way to declare setting is an easy-to-read manner.
   Settings documentation should be the part of the declaration,
   which makes easy to keep it up-to-date.
2. Read settings from any source: be it JSON, YAML, environmental variables, python files or any other sources.
3. Explain a user the resulting settings object: where and how each setting was declared, read from and verified.


Let's start with a basic example:

.. code-block:: python

   from concrete_settings import Settings

   class AppSettings(Settings):

       #: Turns debug mode on/off
       DEBUG: bool = True


This example contains important concepts of ConcreteSettings.
Here we define a settings class with one setting `DEBUG`.
Its type is `bool` and default value is `True`.
The docstring of the setting is defined in a `#: ` comment.

This short form definition is an equivalent to the verbose form:

.. code-block:: python

   from concrete_settings import Settings
   from concrete_settings.validators import ValueTypeValidator

   class AppSettings(Settings):

       DEBUG = Setting(True,
                       type_hint=bool,
                       validators=(ValueTypeValidator(), )
                       doc="Turns debug mode on/off")


.. code-block:: python

       # LATER

       #: Application's unique secret key.
       SECRET_KEY: str = Required

       #: [Deprecated] Secret hash
       SECRET_HASH: str = deprecated(Setting()

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
