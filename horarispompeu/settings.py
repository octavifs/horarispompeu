# encoding: utf-8
# Django settings for horarispompeu project.

DEBUG = True
# Sets up which calendars should be parsed
TERM = "2n Trimestre"
ACADEMIC_YEAR = "2013-14"

TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Octavi Font', 'tavifont@gmail.com'),
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'resources/horaris.sqlite',  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "horarispompeu.com",
    "www.horarispompeu.com",
    "193.145.51.3",
]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = 'resources/calendar/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = 'https://www.horarispompeu.com/calendar/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = 'resources/static/'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Timetable root. Where previous timetable sources (.html from ESUP) will be
# stored.
TIMETABLE_ROOT = 'resources/timetable'

# Additional locations of static files
STATICFILES_DIRS = (
    'timetable/static',
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-ej4b_ibt(^z*p#hp^xjpr%*9=douaw(x3^)s#kq=p@5dqlbo='

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    # The commented lines are default processors that (it seems) are not needed
    # 'django.core.context_processors.i18n',
    # 'django.core.context_processors.media',
    # 'django.core.context_processors.static',
    # 'django.core.context_processors.tz',
    # 'django.contrib.messages.context_processors.messages',
    # 'django.core.context_processors.request',
    'timetable.context_processors.background'
)

ROOT_URLCONF = 'horarispompeu.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'horarispompeu.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    'timetable/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    # Uncomment to enable django_extensions module (adds extra
    # commands to ./manage.py)
    # See http://django-extensions.readthedocs.org/en/latest/
    # for more
    'django_extensions',
    'timetable',
    'gunicorn',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Set up email subject prefix.
EMAIL_SUBJECT_PREFIX = '[HP] '

# Expire session on browser close
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Random backgrounds
from os.path import join
BACKGROUND_IMAGES_PREFIX = join(STATIC_URL, "images")
BACKGROUND_IMAGES = [
    ("IMG_20140103_112135.jpg", "la Xemeneia. Ulldeter (Ripollès)."),
    ("IMG_20140103_111114.jpg", "la Xemeneia. Ulldeter (Ripollès)."),
    ("IMG_20140103_134025.jpg", "Coma del Freser, des de Bastiments. Ulldeter (Ripollès)."),
    ("IMG_20131231_122653.jpg", "Pedraforca i Comabona, des del refugi del Rebost. Serra del Cadí (Berguedà)."),
    ("IMG_20140202_110352.jpg", "cresta del Matagalls, les Agudes al fons. El Montseny (Osona)."),
]

###################################
# VARS TO ADD AS PRIVATE SETTINGS #
###################################

# Email
# EMAIL_USE_TLS = True | False
# EMAIL_PORT = 587
# EMAIL_HOST = 'smtp.hostname.com'
# EMAIL_HOST_USER = 'user@hostname.com'
# EMAIL_HOST_PASSWORD = 'secretPassword'
# DEFAULT_FROM_EMAIL = 'user@hostname.com'
# SERVER_EMAIL = 'user@hostname.com'

# PhantomJS
# AUTO_SUBSCRIPTION_SCRIPT = "/path/to/gcal_addICS.js"
# PHANTOMJS_BIN = "/path/to/bin/phantomjs"

# S3 Backups
# S3_BACKUP = True | False
# AWS_ACCESS_KEY = 'some string'
# AWS_SECRET_KEY = 'some string'
# S3_BUCKET = 'somebucket'

# Supervisord and Nginx config paths
# SUPERVISORD_CONFIG = '/etc/supervisor/conf.d/someconf.conf'
# NGINX_CONFIG = '/etc/nginx/sites-enabled/someconf'
# Import private settings
from settings_private import *
