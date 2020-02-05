.. _startup:

Start me up
###########

Scratch
=======

An extremely short guide to start using Concrete Setting in your application.

I. Define Settings
------------------

As a *developer* of an application, define the settings:

For example, ``my_app/settings_definition.py`` file:

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

   from .settings_definition import ApplicationSettings


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

    from my_app.settings_definition import ApplicationSettings

    def test_settings_definiton():
        ApplicationSettings()

That's it! You are ready to start using Concrete Settings in your programs!


Django Projects
===============

Concrete Settings is shipped with batteries which help bootstrapping
settings in a legacy or a brand new Django project.
First, there is :class:`Django30Settings <concrete_settings.contrib.frameworks.django30.Django30Settings>`
class which reflects Django's `global_settings` definitions.

Django 3.0
----------

New project
...........

Here is an example of how one can start up a new Django application with Concrete Settings.
Let's consider that a project was created by the traditional ``djago-admin.py startproject mysite``.
The good old ``settings.py``. Why not instead have all Django settings in a yaml file instead?

.. code-block:: yaml

   # mysite/django.yml

   SECRET_KEY: 'xnhdv!(nm6f+y^izff1^e#kdy^v3gdgme87j*p)ahs6)t5-(32'

   DEBUG: true

   ALLOWED_HOSTS: []

   INSTALLED_APPS:
     - django.contrib.admin
     - django.contrib.auth
     - django.contrib.contenttypes
     - django.contrib.sessions
     - django.contrib.messages
     - django.contrib.staticfiles

   MIDDLEWARE:
     - django.middleware.security.SecurityMiddleware
     - django.contrib.sessions.middleware.SessionMiddleware
     - django.middleware.common.CommonMiddleware
     - django.middleware.csrf.CsrfViewMiddleware
     - django.contrib.auth.middleware.AuthenticationMiddleware
     - django.contrib.messages.middleware.MessageMiddleware
     - django.middleware.clickjacking.XFrameOptionsMiddleware

   ROOT_URLCONF: mysite.urls

   TEMPLATES:
     - BACKEND: django.template.backends.django.DjangoTemplates
       DIRS: []
       APP_DIRS: true
       OPTIONS:
         context_processors:
           - django.template.context_processors.debug
           - django.template.context_processors.request
           - django.contrib.auth.context_processors.auth
           - django.contrib.messages.context_processors.messages

   WSGI_APPLICATION: mysite.wsgi.application

   DATABASES:
     default:
       ENGINE: django.db.backends.sqlite3
       NAME: '/path/to/db.sqlite3'

   AUTH_PASSWORD_VALIDATORS:
     - NAME: django.contrib.auth.password_validation.UserAttributeSimilarityValidator
     - NAME: django.contrib.auth.password_validation.MinimumLengthValidator
     - NAME: django.contrib.auth.password_validation.CommonPasswordValidator
     - NAME: django.contrib.auth.password_validation.NumericPasswordValidator


   LANGUAGE_CODE: en-us

   TIME_ZONE: UTC

   USE_I18N: true

   USE_L10N: true

   USE_TZ: true

   STATIC_URL: '/static/'


To read this file, ``settings.py`` has to be modified as follows:

.. code-block:: python

   import os

   from concrete_settings import Settings
   from concrete_settings.contrib.frameworks.django30 import Django30Settings

   SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))

   settings = Django30Settings()

   settings.update(SETTINGS_DIR + '/django.yml')

   settings.is_valid(raise_exception=True)
   settings.extract(globals())

Easy, isn't it?


Separate application settings
.............................

Sometimes you need to put application settings to ``settings.py`` to access
them from ``django.conf.settings``. Let's modify ``settings.py`` to separate
Django and application settings:

.. code-block:: python

   import os

   from concrete_settings import Settings
   from concrete_settings.contrib.frameworks.django30 import Django30Settings

   SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))


   class ApplicationSettings(Settings):
       GREETING_MESSAGE: str = 'Welcome'


   class SiteSettings(ApplicationSettings, Django30Settings):
       pass


   settings = SiteSettings()

   settings.update(SETTINGS_DIR + '/django.yml')
   settings.update(SETTINGS_DIR + '/application.yml')

   settings.is_valid(raise_exception=True)
   settings.extract(globals())

And ``application.yml`` is:

.. code-block:: yaml

  GREETING_MESSAGE: Welcome, Concrete Settings User!
