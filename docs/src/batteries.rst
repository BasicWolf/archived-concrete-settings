.. _contrib:

Batteries
#########

Powerful batteries for bootstrapping Concrete Settings in your projects.


Sources
=======

The built-in sources are automatically registered when ``concrete_settings``
is imported. This means that calling for example
:meth:`setting.update('/path/to/settings.yaml') <concrete_settings.Settings.update>`
would automatically invoke :class:`YamlSource <concrete_settings.contrib.sources.YamlSource>`.

Most of the provided sources read the files into memory and store them
as Python dicts. Updating a setting from such source ends up in
querying a dict like: ``internal_dict[setting_name]``.

.. autoclass:: concrete_settings.contrib.sources.EnvVarSource

   Updates settings from environmental variables.

   A nested setting's parent attribute name is expected to be in
   upper case and separated by "_". For example, consider that
   an environmental variable ``DB_HOST`` is set as follows:

   .. code-block:: bash

      export DB_HOST=my-db-server.com

   And here is a nested settings structure
   updated from environmental variables source:

   .. testsetup:: batteries_env_var_source

      import os
      os.environ['DB_HOST'] = 'my-db-server.com'

   .. testcode:: batteries_env_var_source

      from concrete_settings import Settings
      from concrete_settings.contrib.sources import EnvVarSource

      class DatabaseSettings(Settings):
          HOST: str = 'localhost'

      class AppSettings(Settings):
          DB = DatabaseSettings()

      app_settings = AppSettings()
      app_settings.update(EnvVarSource())
      print(app_settings.DB.HOST)

   Output:

   .. testoutput:: batteries_env_var_source

      my-db-server.com


.. autoclass:: concrete_settings.contrib.sources.PythonSource

   Allows updating settings from Python files (``*.py``) with
   settings corresponding to top-level variables, such as:

   .. code-block::

      ADMIN_EMAIL = 'alex@example.com'

      DEBUG = True

      # can be read as nested settings
      DB = {
          HOST: '127.0.0.1'
          PORT: 5432
      }


.. autoclass:: concrete_settings.contrib.sources.YamlSource

   Allows updating settings from YAML files (``*.yml; *.yaml``):

   .. code-block:: yaml

      DEBUG: true

      ADMIN_EMAIL: alex@example.com

      DB:
          HOST: 127.0.0.1
          PORT: 5432


.. autoclass:: concrete_settings.contrib.sources.JsonSource

   Allows updating settings from JSON files (``*.js; *.json``)

   .. code-block:: json

      {
         "DEBUG": true,

         "ADMIN_EMAIL": "alex@example.com",

         "DB": {
             "HOST": "127.0.0.1"
             "PORT": 5432
         }
      }


Frameworks
==========


Django
------

.. module:: concrete_settings.contrib.frameworks.django30

.. autoclass:: Django30Settings

   Parent class for Django 3.0 -based settings.
   The default values correspond to the default values of
   ``django.conf.global_settings``.
