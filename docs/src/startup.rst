.. _startup:

Start me up
###########

Scratch
=======

An extremely short guide to start using Concrete Setting in your application.

I. Define Settings
------------------

As a *developer* of an application, define the settings:

For example, ``my_app/app_settings.py`` file:

.. testcode:: start-me-up

   from concrete_settings import Settings

   class ApplicationSettings(Settings):
       #: Turns on / off debug mode
       DEBUG: bool = False

II. Think of an end-user
------------------------

Provide a conventient way of entering the application settings to an end-user.
For example  via a ``.yaml`` file passed as a command-line argument:


.. code-block::

   # my_app/main.py

   import os
   import sys

   from .app_settings import ApplicationSettings


   def main():
       """Usage:


       python main.py /path/to/settings.yaml
       """
       settings = ApplicationSettings()
       if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
           print(f'Reading settings from {sys.argv[1]}')
           settings.update(sys.argv[1])

       # validate the settings,
       # raise exception if something is invalid
       settings.is_valid(raise_exception=True)

       # start application with settings
       ...
       if settings.DEBUG:
           ...


.. code-block:: yaml

   # settings.yaml

   DEBUG: true


.. testcode:: start-me-up
   :hide:

   import os
   import sys

   def main():
       settings = ApplicationSettings()
       if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
           print(f'Reading settings from {sys.argv[1]}')
           settings.update(sys.argv[1])

       # validate the settings,
       # raise exception if something is invalid
       settings.is_valid(raise_exception=True)

       # start application with settings
       ...
       if settings.DEBUG:
           ...

   main()

III. Remember to test settings object definition
------------------------------------------------

.. code-block::

    # we love pytest!

    from my_app.app_settings import ApplicationSettings

    def test_settings_definiton():
        ApplicationSettings()

That's it! You are ready to start using Concrete Settings in your programs!


Django
======

Concrete Settings is shipped with batteries which help bootstrapping
settings in a legacy or a brand new Django project.
:class:`Django30Settings <concrete_settings.contrib.frameworks.django30.Django30Settings>`
class reflects Django 3.0 `global_settings` definitions and allows quick
integration with new and legacy projects.


New projects
------------

Here is an example of starting up a new Django application with Concrete Settings.
Let's consider that a project was created by the traditional ``djago-admin.py startproject mysite``.
The project settings are defined in the good old ``settings.py``.
Why not have all Django settings in a YAML file instead?
(:download:`full example source <examples/django30_template.yml>`)

.. code-block:: yaml

   # mysite/django.yml

   SECRET_KEY: 'xnhdv!(nm6f+y^izff1^e#kdy^v3gdgme87j*p)ahs6)t5-(32'

   DEBUG: true

   ALLOWED_HOSTS: []

   INSTALLED_APPS:
     - django.contrib.admin
     - django.contrib.auth
     - ...

   ...

   ROOT_URLCONF: mysite.urls

   ...

   STATIC_URL: '/static/'


To read this file, ``settings.py`` can be modified as follows:

.. testsetup:: read-django-yml

   __file__ = '/tmp/django.yml'

   with open('/tmp/django.yml', 'w') as f:
       f.write('ROOT_URLCONF: mysite.urls')


.. testcode:: read-django-yml

   import os

   from concrete_settings import Settings
   from concrete_settings.contrib.frameworks.django30 import Django30Settings

   SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))

   settings = Django30Settings()

   # Read settings from djano.yml
   settings.update(SETTINGS_DIR + '/django.yml')

   # Validate settings
   settings.is_valid(raise_exception=True)

   # extract settings to module's global scope
   # so that Django can read them
   settings.extract_to(globals())


.. testcleanup:: quickstart-json-source

   import os
   os.remove('/tmp/django.yml')

Easy, isn't it?


Separate application settings
-----------------------------

Developers often put application settings to a site's ``settings.py``
which leads to mixing up Django and Application settings.
Let's put application settings definiton to a separate file
``application_settings.py``:


.. testcode:: read-django-application-yml

   # mysite/application_settings.py

   from concrete_settings import Settings

   class ApplicationSettings(Settings):
       GREETING_MESSAGE: str = 'Welcome'

A corresponding ``application.yml`` would be:

.. code-block:: yaml

   # mysite/application.yml

   GREETING_MESSAGE: Welcome, Concrete Settings User!


Finally we can combine Django and application settings in ``settings.py``
and load the settings from ``django.yml`` and ``application.yml``:


.. testsetup:: read-django-application-yml

   __file__ = '/tmp/django.yml'

   with open('/tmp/django.yml', 'w') as f:
       f.write('ROOT_URLCONF: mysite.urls')

   with open('/tmp/application.yml', 'w') as f:
       f.write('')


.. testcode:: read-django-application-yml
   :hide:

   __file__ = '/tmp/django.yml'

   # Note, this should be the same as code-block below.
   # Duplicating since unable to import ApplicationSettings relatively

   from concrete_settings.contrib.frameworks.django30 import Django30Settings

   SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))

   class SiteSettings(ApplicationSettings, Django30Settings):
       def validate(self):
           super().validate()
           ApplicationSettings.validate(self)
           Django30Settings.validate(self)

   settings = SiteSettings()

   settings.update(SETTINGS_DIR + '/django.yml')
   settings.update(SETTINGS_DIR + '/application.yml')

   settings.is_valid(raise_exception=True)
   settings.extract_to(globals())

.. code-block::

   # settings.py

   import os

   from concrete_settings.contrib.frameworks.django30 import Django30Settings

   from .application_settings import AppliactionSettings


   SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))


   class SiteSettings(ApplicationSettings, Django30Settings):
       def validate(self):
           super().validate()
           ApplicationSettings.validate(self)
           Django30Settings.validate(self)

   settings = SiteSettings()

   settings.update(SETTINGS_DIR + '/django.yml')
   settings.update(SETTINGS_DIR + '/application.yml')

   settings.is_valid(raise_exception=True)
   settings.extract_to(globals())



Legacy projects
---------------

Existing Django projects' settings can be gradually migrated to Concrete Settings
without modifying the existing configuration files at all!

The basic idea is to import the original settings attributes via
``from settings import *``, then process the ``globals()`` with
Concrete Settings:

.. code-block:: python

   # mysite/new_settings.py
   # remember to update DJANGO_SETTINGS_MODULE

   import os

   from concrete_settings.contrib.frameworks.django30 import Django30Settings
   from .settings import *  # import all existing application settings

   SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))

   settings = Django30Settings()

   # load variables imported from settings.py
   settings.update(globals())

   settings.is_valid(raise_exception=True)

   settings.extract_to(globals())

Start migrating application settings by defining an empty
``Settings`` class in ``application_settings.py``:

.. code-block:: python

   from concrete_settings import Settings

   class ApplicationSettings(Settings):
       ...

Update ``new_settings.py`` to separate Django and application settings:


.. code-block:: python

   # new_settings.py

   import os

   from concrete_settings.contrib.frameworks.django30 import Django30Settings

   from .application_settings import ApplicationSettings

   from .settings import *

   SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))


   class SiteSettings(ApplicationSettings, Django30Settings):
       def validate(self):
           super().validate()
           ApplicationSettings.validate(self)
           Django30Settings.validate(self)


   settings = SiteSettings()

   settings.update(globals())
   settings.update(SETTINGS_DIR + '/application.yml')  # optional

   settings.is_valid(raise_exception=True)
   settings.extract_to(globals())
