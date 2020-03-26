from typing import Dict, List, Tuple, Optional

from concrete_settings import Settings, Undefined

# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
from concrete_settings.contrib.behaviors import required


# flake8: noqa


def gettext_noop(s):
    return s


class Django30Settings(Settings):
    DEBUG: bool = False

    #: Whether the framework should propagate raw exceptions rather than catching
    #: them. This is useful under some testing situations and should never be used
    #: on a live site.
    DEBUG_PROPAGATE_EXCEPTIONS: bool = False

    #: People who get code error notifications.
    #: In the format [
    #     ('Full Name', 'email@example.com'),
    #     ('Full Name', 'anotheremail@example.com')
    # ]
    ADMINS: List[Tuple[str, str]] = []

    #: List of IP addresses, as strings, that:
    #:   * See debug comments, when DEBUG is true
    #:   * Receive x-headers
    INTERNAL_IPS: List = []

    #: Hosts/domain names that are valid for this site.
    #: "*" matches anything, ".example.com" matches example.com and all subdomains
    ALLOWED_HOSTS: List = []

    #: Local time zone for this installation. All choices can be found here:
    #: https://en.wikipedia.org/wiki/List_of_tz_zones_by_name (although not all
    #: systems may support all possibilities). When USE_TZ is True, this is
    #: interpreted as the default user time zone.
    TIME_ZONE: str = 'America/Chicago'

    #: If you set this to True, Django will use timezone-aware datetimes.
    USE_TZ: bool = False

    #: Language code for this installation. All choices can be found here:
    #: http://www.i18nguy.com/unicode/language-identifiers.html
    LANGUAGE_CODE: str = 'en-us'

    #: Languages we provide translations for, out of the box.
    LANGUAGES: List[Tuple] = [
        ('af', gettext_noop('Afrikaans')),
        ('ar', gettext_noop('Arabic')),
        ('ast', gettext_noop('Asturian')),
        ('az', gettext_noop('Azerbaijani')),
        ('bg', gettext_noop('Bulgarian')),
        ('be', gettext_noop('Belarusian')),
        ('bn', gettext_noop('Bengali')),
        ('br', gettext_noop('Breton')),
        ('bs', gettext_noop('Bosnian')),
        ('ca', gettext_noop('Catalan')),
        ('cs', gettext_noop('Czech')),
        ('cy', gettext_noop('Welsh')),
        ('da', gettext_noop('Danish')),
        ('de', gettext_noop('German')),
        ('dsb', gettext_noop('Lower Sorbian')),
        ('el', gettext_noop('Greek')),
        ('en', gettext_noop('English')),
        ('en-au', gettext_noop('Australian English')),
        ('en-gb', gettext_noop('British English')),
        ('eo', gettext_noop('Esperanto')),
        ('es', gettext_noop('Spanish')),
        ('es-ar', gettext_noop('Argentinian Spanish')),
        ('es-co', gettext_noop('Colombian Spanish')),
        ('es-mx', gettext_noop('Mexican Spanish')),
        ('es-ni', gettext_noop('Nicaraguan Spanish')),
        ('es-ve', gettext_noop('Venezuelan Spanish')),
        ('et', gettext_noop('Estonian')),
        ('eu', gettext_noop('Basque')),
        ('fa', gettext_noop('Persian')),
        ('fi', gettext_noop('Finnish')),
        ('fr', gettext_noop('French')),
        ('fy', gettext_noop('Frisian')),
        ('ga', gettext_noop('Irish')),
        ('gd', gettext_noop('Scottish Gaelic')),
        ('gl', gettext_noop('Galician')),
        ('he', gettext_noop('Hebrew')),
        ('hi', gettext_noop('Hindi')),
        ('hr', gettext_noop('Croatian')),
        ('hsb', gettext_noop('Upper Sorbian')),
        ('hu', gettext_noop('Hungarian')),
        ('hy', gettext_noop('Armenian')),
        ('ia', gettext_noop('Interlingua')),
        ('id', gettext_noop('Indonesian')),
        ('io', gettext_noop('Ido')),
        ('is', gettext_noop('Icelandic')),
        ('it', gettext_noop('Italian')),
        ('ja', gettext_noop('Japanese')),
        ('ka', gettext_noop('Georgian')),
        ('kab', gettext_noop('Kabyle')),
        ('kk', gettext_noop('Kazakh')),
        ('km', gettext_noop('Khmer')),
        ('kn', gettext_noop('Kannada')),
        ('ko', gettext_noop('Korean')),
        ('lb', gettext_noop('Luxembourgish')),
        ('lt', gettext_noop('Lithuanian')),
        ('lv', gettext_noop('Latvian')),
        ('mk', gettext_noop('Macedonian')),
        ('ml', gettext_noop('Malayalam')),
        ('mn', gettext_noop('Mongolian')),
        ('mr', gettext_noop('Marathi')),
        ('my', gettext_noop('Burmese')),
        ('nb', gettext_noop('Norwegian Bokmål')),
        ('ne', gettext_noop('Nepali')),
        ('nl', gettext_noop('Dutch')),
        ('nn', gettext_noop('Norwegian Nynorsk')),
        ('os', gettext_noop('Ossetic')),
        ('pa', gettext_noop('Punjabi')),
        ('pl', gettext_noop('Polish')),
        ('pt', gettext_noop('Portuguese')),
        ('pt-br', gettext_noop('Brazilian Portuguese')),
        ('ro', gettext_noop('Romanian')),
        ('ru', gettext_noop('Russian')),
        ('sk', gettext_noop('Slovak')),
        ('sl', gettext_noop('Slovenian')),
        ('sq', gettext_noop('Albanian')),
        ('sr', gettext_noop('Serbian')),
        ('sr-latn', gettext_noop('Serbian Latin')),
        ('sv', gettext_noop('Swedish')),
        ('sw', gettext_noop('Swahili')),
        ('ta', gettext_noop('Tamil')),
        ('te', gettext_noop('Telugu')),
        ('th', gettext_noop('Thai')),
        ('tr', gettext_noop('Turkish')),
        ('tt', gettext_noop('Tatar')),
        ('udm', gettext_noop('Udmurt')),
        ('uk', gettext_noop('Ukrainian')),
        ('ur', gettext_noop('Urdu')),
        ('uz', gettext_noop('Uzbek')),
        ('vi', gettext_noop('Vietnamese')),
        ('zh-hans', gettext_noop('Simplified Chinese')),
        ('zh-hant', gettext_noop('Traditional Chinese')),
    ]

    #: Languages using BiDi (right-to-left) layout
    LANGUAGES_BIDI: List[str] = ["he", "ar", "fa", "ur"]

    #: If you set this to False, Django will make some optimizations so as not
    #: to load the internationalization machinery.
    USE_I18N: bool = True
    LOCALE_PATHS: List = []

    # Settings for language cookie
    LANGUAGE_COOKIE_NAME: str = 'django_language'
    #: The age of the language cookie, in seconds.
    LANGUAGE_COOKIE_AGE: Optional[int] = None
    #: The domain to use for the language cookie.
    #: Set this to a string such as "example.com"
    #: for cross-domain cookies, or use None for a standard domain cookie.
    LANGUAGE_COOKIE_DOMAIN: Optional[str] = None
    LANGUAGE_COOKIE_PATH: str = '/'
    LANGUAGE_COOKIE_SECURE: bool = False
    LANGUAGE_COOKIE_HTTPONLY: bool = False
    LANGUAGE_COOKIE_SAMESITE: Optional[str] = None

    #: If you set this to True, Django will format dates, numbers and calendars
    #: according to user current locale.
    USE_L10N: bool = False

    #: Not-necessarily-technical managers of the site. They get broken link
    #: notifications and other various emails.
    MANAGERS: List[Tuple[str, str]] = ADMINS

    #: Default charset to use for all HttpResponse objects, if a MIME type isn't
    #: manually specified. It's used to construct the Content-Type header.
    DEFAULT_CHARSET: str = 'utf-8'

    #: Encoding of files read from disk (template and initial SQL files).
    FILE_CHARSET: str = 'utf-8'

    #: Email address that error messages come from.
    SERVER_EMAIL: str = 'root@localhost'

    #: Database connection info. If left empty, will default to the dummy backend.
    DATABASES: Dict = {}

    #: Classes used to implement DB routing behavior.
    DATABASE_ROUTERS: list = []

    #: The email backend to use. For possible shortcuts see django.core.mail.
    #: The default is to use the SMTP backend.
    #: Third-party backends can be specified by providing a Python path
    #: to a module that defines an EmailBackend class.
    EMAIL_BACKEND: str = 'django.core.mail.backends.smtp.EmailBackend'

    #: Host for sending email.
    EMAIL_HOST: str = 'localhost'

    #: Port for sending email.
    EMAIL_PORT: int = 25

    #: Whether to send SMTP 'Date' header in the local time zone or in UTC.
    EMAIL_USE_LOCALTIME: bool = False

    #: Optional SMTP authentication information for EMAIL_HOST.
    EMAIL_HOST_USER: str = ''
    EMAIL_HOST_PASSWORD: str = ''
    EMAIL_USE_TLS: bool = False
    EMAIL_USE_SSL: bool = False
    #: If EMAIL_USE_SSL or EMAIL_USE_TLS is True, you can optionally specify
    #: the path to a PEM-formatted certificate chain file to use for the
    #: SSL connection.
    EMAIL_SSL_CERTFILE: Optional[str] = None
    #: If EMAIL_USE_SSL or EMAIL_USE_TLS is True, you can optionally specify
    #: the path to a PEM-formatted private key file to use for the
    #: SSL connection.
    EMAIL_SSL_KEYFILE: Optional[str] = None
    #: Specifies a timeout in seconds for blocking operations like the connection
    #: attempt.
    EMAIL_TIMEOUT: Optional[int] = None

    #: List of strings representing installed apps.
    INSTALLED_APPS: List = []

    TEMPLATES: List = []

    #: Default form rendering class.
    FORM_RENDERER: str = 'django.forms.renderers.DjangoTemplates'

    #: Default email address to use for various automated correspondence from
    #: the site managers.
    DEFAULT_FROM_EMAIL: str = 'webmaster@localhost'

    #: Subject-line prefix for email messages send with django.core.mail.mail_admins
    #: or ...mail_managers.  Make sure to include the trailing space.
    EMAIL_SUBJECT_PREFIX: str = '[Django] '

    #: Whether to append trailing slashes to URLs.
    APPEND_SLASH: bool = True

    #: Whether to prepend the "www." subdomain to URLs that don't have it.
    PREPEND_WWW: bool = False

    #: Override the server-derived value of SCRIPT_NAME
    FORCE_SCRIPT_NAME: Optional[str] = None

    #: List of compiled regular expression objects representing User-Agent strings
    #: that are not allowed to visit any page, systemwide. Use this for bad
    #: robots/crawlers. Here are a few examples:
    #:     import re
    #:     DISALLOWED_USER_AGENTS = [
    #:         re.compile(r'^NaverBot.*'),
    #:         re.compile(r'^EmailSiphon.*'),
    #:         re.compile(r'^SiteSucker.*'),
    #:         re.compile(r'^sohu-search'),
    #:     ]
    DISALLOWED_USER_AGENTS: List = []

    ABSOLUTE_URL_OVERRIDES: Dict = {}

    #: List of compiled regular expression objects representing URLs that need not
    #: be reported by BrokenLinkEmailsMiddleware. Here are a few examples:
    #:    import re
    #:    IGNORABLE_404_URLS = [
    #:        re.compile(r'^/apple-touch-icon.*\.png$'),
    #:        re.compile(r'^/favicon.ico$'),
    #:        re.compile(r'^/robots.txt$'),
    #:        re.compile(r'^/phpmyadmin/'),
    #:        re.compile(r'\.(cgi|php|pl)$'),
    #:    ]
    IGNORABLE_404_URLS: List = []

    #: A secret key for this particular Django installation. Used in secret-key
    #: hashing algorithms. Set this in your settings, or Django will complain
    #: loudly.
    SECRET_KEY: str = ''

    #: Default file storage mechanism that holds media.
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    #: Absolute filesystem path to the directory that will hold user-uploaded files.
    #: Example: "/var/www/example.com/media/"
    MEDIA_ROOT: str = ''

    #: URL that handles the media served from MEDIA_ROOT.
    #: Examples: "http://example.com/media/", "http://media.example.com/"
    MEDIA_URL: str = ''

    #: Absolute path to the directory static files should be collected to.
    #: Example: "/var/www/example.com/static/"
    STATIC_ROOT: Optional[str] = None

    #: URL that handles the static files served from STATIC_ROOT.
    #: Example: "http://example.com/static/", "http://static.example.com/"
    STATIC_URL: Optional[str] = None

    #: List of upload handler classes to be applied in order.
    FILE_UPLOAD_HANDLERS: List[str] = [
        'django.core.files.uploadhandler.MemoryFileUploadHandler',
        'django.core.files.uploadhandler.TemporaryFileUploadHandler',
    ]

    #: Maximum size, in bytes, of a request before it will be streamed to the
    #: file system instead of into memory.
    FILE_UPLOAD_MAX_MEMORY_SIZE: int = 2621440  # i.e. 2.5 MB

    #: Maximum size in bytes of request data (excluding file uploads) that will be
    #: read before a SuspiciousOperation (RequestDataTooBig) is raised.
    DATA_UPLOAD_MAX_MEMORY_SIZE: int = 2621440  # i.e. 2.5 MB

    #: Maximum number of GET/POST parameters that will be read before a
    #: SuspiciousOperation (TooManyFieldsSent) is raised.
    DATA_UPLOAD_MAX_NUMBER_FIELDS: int = 1000

    #: Directory in which upload streamed files will be temporarily saved. A value of
    #: `None` will make Django use the operating system's default temporary directory
    #: (i.e. "/tmp" on *nix systems).
    FILE_UPLOAD_TEMP_DIR: Optional[str] = None

    #: The numeric mode to set newly-uploaded files to. The value should be a mode
    #: you'd pass directly to os.chmod;
    # see https://docs.python.org/library/os.html#files-and-directories.
    FILE_UPLOAD_PERMISSIONS: int = 0o644

    #: The numeric mode to assign to newly-created directories, when uploading files.
    #: The value should be a mode as you'd pass to os.chmod;
    #: see https://docs.python.org/library/os.html#files-and-directories.
    FILE_UPLOAD_DIRECTORY_PERMISSIONS: Optional[int] = None

    #: Python module path where user will place custom format definition.
    #: The directory where this setting is pointing should contain subdirectories
    #: named as the locales, containing a formats.py file
    #: (i.e. "myproject.locale" for myproject/locale/en/formats.py etc. use)
    FORMAT_MODULE_PATH: Optional[str] = None

    #: Default formatting for date objects. See all available format strings here:
    #: https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
    DATE_FORMAT: str = 'N j, Y'

    #: Default formatting for datetime objects. See all available format strings here:
    #: https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
    DATETIME_FORMAT: str = 'N j, Y, P'

    #: Default formatting for time objects. See all available format strings here:
    #: https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
    TIME_FORMAT: str = 'P'

    #: Default formatting for date objects when only the year and month are relevant.
    #: See all available format strings here:
    #: https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
    YEAR_MONTH_FORMAT: str = 'F Y'

    #: Default formatting for date objects when only the month and day are relevant.
    #: See all available format strings here:
    #: https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
    MONTH_DAY_FORMAT: str = 'F j'

    #: Default short formatting for date objects. See all available format strings here:
    #: https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
    SHORT_DATE_FORMAT: str = 'm/d/Y'

    #: Default short formatting for datetime objects.
    #: See all available format strings here:
    #: https://docs.djangoproject.com/en/dev/ref/templates/builtins/#date
    SHORT_DATETIME_FORMAT: str = 'm/d/Y P'

    #: Default formats to be used when parsing dates from input boxes, in order
    #: See all available format string here:
    #: https://docs.python.org/library/datetime.html#strftime-behavior
    #: * Note that these format strings are different from the ones to display dates
    DATE_INPUT_FORMATS: List[str] = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%m/%d/%y',  # '2006-10-25', '10/25/2006', '10/25/06'
        '%b %d %Y',
        '%b %d, %Y',  # 'Oct 25 2006', 'Oct 25, 2006'
        '%d %b %Y',
        '%d %b, %Y',  # '25 Oct 2006', '25 Oct, 2006'
        '%B %d %Y',
        '%B %d, %Y',  # 'October 25 2006', 'October 25, 2006'
        '%d %B %Y',
        '%d %B, %Y',  # '25 October 2006', '25 October, 2006'
    ]

    #: Default formats to be used when parsing times from input boxes, in order
    #: See all available format string here:
    #: https://docs.python.org/library/datetime.html#strftime-behavior
    #: * Note that these format strings are different from the ones to display dates
    TIME_INPUT_FORMATS: List[str] = [
        '%H:%M:%S',  # '14:30:59'
        '%H:%M:%S.%f',  # '14:30:59.000200'
        '%H:%M',  # '14:30'
    ]

    #: Default formats to be used when parsing dates and times from input boxes,
    #: in order
    #: See all available format string here:
    #: https://docs.python.org/library/datetime.html#strftime-behavior
    #: * Note that these format strings are different from the ones to display dates
    DATETIME_INPUT_FORMATS: List[str] = [
        '%Y-%m-%d %H:%M:%S',  # '2006-10-25 14:30:59'
        '%Y-%m-%d %H:%M:%S.%f',  # '2006-10-25 14:30:59.000200'
        '%Y-%m-%d %H:%M',  # '2006-10-25 14:30'
        '%Y-%m-%d',  # '2006-10-25'
        '%m/%d/%Y %H:%M:%S',  # '10/25/2006 14:30:59'
        '%m/%d/%Y %H:%M:%S.%f',  # '10/25/2006 14:30:59.000200'
        '%m/%d/%Y %H:%M',  # '10/25/2006 14:30'
        '%m/%d/%Y',  # '10/25/2006'
        '%m/%d/%y %H:%M:%S',  # '10/25/06 14:30:59'
        '%m/%d/%y %H:%M:%S.%f',  # '10/25/06 14:30:59.000200'
        '%m/%d/%y %H:%M',  # '10/25/06 14:30'
        '%m/%d/%y',  # '10/25/06'
    ]

    #: First day of week, to be used on calendars
    #: 0 means Sunday, 1 means Monday...
    FIRST_DAY_OF_WEEK: int = 0

    #: Decimal separator symbol
    DECIMAL_SEPARATOR: str = '.'

    #: Boolean that sets whether to add thousand separator when formatting numbers
    USE_THOUSAND_SEPARATOR: bool = False

    #: Number of digits that will be together, when splitting them by
    #: THOUSAND_SEPARATOR. 0 means no grouping, 3 means splitting by thousands...
    NUMBER_GROUPING: int = 0

    #: Thousand separator symbol
    THOUSAND_SEPARATOR: str = ','

    #: The tablespaces to use for each model when not specified otherwise.
    DEFAULT_TABLESPACE: str = ''
    DEFAULT_INDEX_TABLESPACE: str = ''

    #: Default X-Frame-Options header value
    X_FRAME_OPTIONS: str = 'DENY'

    USE_X_FORWARDED_HOST: bool = False
    USE_X_FORWARDED_PORT: bool = False

    #: The Python dotted path to the WSGI application that Django's internal server
    #: (runserver) will use. If `None`, the return value of
    #: 'django.core.wsgi.get_wsgi_application' is used, thus preserving the same
    #: behavior as previous versions of Django. Otherwise this should point to an
    #: actual WSGI application object.
    WSGI_APPLICATION: Optional[str] = None

    #: If your Django app is behind a proxy that sets a header to specify secure
    #: connections, AND that proxy ensures that user-submitted headers with the
    #: same name are ignored (so that people can't spoof it), set this value to
    #: a tuple of (header_name, header_value). For any requests that come in with
    #: that header/value, request.is_secure() will return True.
    #: WARNING! Only set this if you fully understand what you're doing. Otherwise,
    #: you may be opening yourself up to a security risk.
    SECURE_PROXY_SSL_HEADER: Optional[Tuple] = None

    ##############
    # MIDDLEWARE #
    ##############

    # List of middleware to use. Order is important; in the request phase, these
    # middleware will be applied in the order given, and in the response
    # phase the middleware will be applied in reverse order.
    MIDDLEWARE: List[str] = []

    ############
    # SESSIONS #
    ############

    #: Cache to store session data if using the cache session backend.
    SESSION_CACHE_ALIAS: str = 'default'
    #: Cookie name. This can be whatever you want.
    SESSION_COOKIE_NAME: str = 'sessionid'
    #: Age of cookie, in seconds (default: 2 weeks).
    SESSION_COOKIE_AGE: int = 60 * 60 * 24 * 7 * 2
    #: A string like "example.com", or None for standard domain cookie.
    SESSION_COOKIE_DOMAIN: Optional[str] = None
    #: Whether the session cookie should be secure (https:// only).
    SESSION_COOKIE_SECURE: bool = False
    #: The path of the session cookie.
    SESSION_COOKIE_PATH: str = '/'
    #: Whether to use the HttpOnly flag.
    SESSION_COOKIE_HTTPONLY: bool = True
    #: Whether to set the flag restricting cookie leaks on cross-site requests.
    #: This can be 'Lax', 'Strict', or None to disable the flag.
    SESSION_COOKIE_SAMESITE: Optional[str] = 'Lax'
    #: Whether to save the session data on every request.
    SESSION_SAVE_EVERY_REQUEST: bool = False
    #: Whether a user's session cookie expires when the Web browser is closed.
    SESSION_EXPIRE_AT_BROWSER_CLOSE: bool = False
    #: The module to store session data
    SESSION_ENGINE: str = 'django.contrib.sessions.backends.db'
    #: Directory to store session files if using the file session module. If None,
    #: the backend will use a sensible default.
    SESSION_FILE_PATH: Optional[str] = None
    #: class to serialize session data
    SESSION_SERIALIZER: str = 'django.contrib.sessions.serializers.JSONSerializer'

    #########
    # CACHE #
    #########

    # The cache backends to use.
    CACHES: dict = {
        'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}
    }
    CACHE_MIDDLEWARE_KEY_PREFIX: str = ''
    CACHE_MIDDLEWARE_SECONDS: int = 600
    CACHE_MIDDLEWARE_ALIAS: str = 'default'

    ##################
    # AUTHENTICATION #
    ##################

    AUTH_USER_MODEL: str = 'auth.User'

    AUTHENTICATION_BACKENDS: List[str] = ['django.contrib.auth.backends.ModelBackend']

    LOGIN_URL: str = '/accounts/login/'

    LOGIN_REDIRECT_URL: str = '/accounts/profile/'

    LOGOUT_REDIRECT_URL: Optional[str] = None

    #: The number of days a password reset link is valid for
    PASSWORD_RESET_TIMEOUT_DAYS: int = 3

    #: The first hasher in this list is the preferred algorithm.  any
    #: password using different algorithms will be converted automatically
    #: upon login
    PASSWORD_HASHERS: List[str] = [
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
        'django.contrib.auth.hashers.Argon2PasswordHasher',
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    ]

    AUTH_PASSWORD_VALIDATORS: List[Dict] = []

    ###########
    # SIGNING #
    ###########

    SIGNING_BACKEND: str = 'django.core.signing.TimestampSigner'

    ########
    # CSRF #
    ########

    #: Dotted path to callable to be used as view when a request is
    #: rejected by the CSRF middleware.
    CSRF_FAILURE_VIEW: str = 'django.views.csrf.csrf_failure'

    # Settings for CSRF cookie.
    CSRF_COOKIE_NAME: str = 'csrftoken'
    CSRF_COOKIE_AGE: int = 60 * 60 * 24 * 7 * 52
    CSRF_COOKIE_DOMAIN: Optional[str] = None
    CSRF_COOKIE_PATH: str = '/'
    CSRF_COOKIE_SECURE: bool = False
    CSRF_COOKIE_HTTPONLY: bool = False
    CSRF_COOKIE_SAMESITE: Optional[str] = 'Lax'
    CSRF_HEADER_NAME: str = 'HTTP_X_CSRFTOKEN'
    CSRF_TRUSTED_ORIGINS: List[str] = []
    CSRF_USE_SESSIONS: bool = False

    ############
    # MESSAGES #
    ############

    #: Class to use as messages backend
    MESSAGE_STORAGE: str = 'django.contrib.messages.storage.fallback.FallbackStorage'

    # Default values of MESSAGE_LEVEL and MESSAGE_TAGS are defined within
    # django.contrib.messages to avoid imports in this settings file.

    ###########
    # LOGGING #
    ###########

    #: The callable to use to configure logging
    LOGGING_CONFIG: str = 'logging.config.dictConfig'

    #: Custom logging configuration.
    LOGGING: Dict = {}

    #: Default exception reporter filter class used in case none has been
    #: specifically assigned to the HttpRequest instance.
    DEFAULT_EXCEPTION_REPORTER_FILTER: str = 'django.views.debug.SafeExceptionReporterFilter'

    ###########
    # TESTING #
    ###########

    #: The name of the class to use to run the test suite
    TEST_RUNNER: str = 'django.test.runner.DiscoverRunner'

    #: Apps that don't need to be serialized at test database creation time
    #: (only apps with migrations are to start with)
    TEST_NON_SERIALIZED_APPS: List[str] = []

    ############
    # FIXTURES #
    ############

    #: The list of directories to search for fixtures
    FIXTURE_DIRS: List[str] = []

    ###############
    # STATICFILES #
    ###############

    #: A list of locations of additional static files
    STATICFILES_DIRS: List[str] = []

    #: The default file storage backend used during the build process
    STATICFILES_STORAGE: str = 'django.contrib.staticfiles.storage.StaticFilesStorage'

    #: List of finder classes that know how to find static files in
    #: various locations.
    STATICFILES_FINDERS: List[str] = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        # 'django.contrib.staticfiles.finders.DefaultStorageFinder',
    ]

    ##############
    # MIGRATIONS #
    ##############

    #: Migration module overrides for apps, by app label.
    MIGRATION_MODULES: Dict[str, str] = {}

    #################
    # SYSTEM CHECKS #
    #################

    #: List of all issues generated by system checks that should be silenced. Light
    #: issues like warnings, infos or debugs will not generate a message. Silencing
    #: serious issues like errors and criticals does not result in hiding the
    #: message, but Django will not stop you from e.g. running server.
    SILENCED_SYSTEM_CHECKS: List[str] = []

    #######################
    # SECURITY MIDDLEWARE #
    #######################
    SECURE_BROWSER_XSS_FILTER: bool = False
    SECURE_CONTENT_TYPE_NOSNIFF: bool = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS: bool = False
    SECURE_HSTS_PRELOAD: bool = False
    SECURE_HSTS_SECONDS: int = 0
    SECURE_REDIRECT_EXEMPT: List[str] = []
    SECURE_REFERRER_POLICY: Optional[str] = None
    SECURE_SSL_HOST: Optional[str] = None
    SECURE_SSL_REDIRECT: bool = False

    ##############
    # Undefined
    ##############

    #: A string representing the full Python import path to your root URLconf,
    #: for example "mydjangoapps.urls".
    ROOT_URLCONF: str = Undefined @ required
