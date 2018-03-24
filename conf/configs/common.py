"""
Settings common to all deployment methods.
"""

import os
import socket

__author__ = 'Alex Laird'
__copyright__ = 'Copyright 2018, Alex Laird'
__version__ = '0.1.0'

# Define the base working directory of the application
BASE_DIR = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', '..'))

# ############################
# Project configuration
# ############################

# Project information

PROJECT_NAME = os.environ.get('CHACHATWILIO_NAME')

PROJECT_HOST = os.environ.get('CHACHATWILIO_HOST')

# Version information

PROJECT_VERSION = __version__

#############################
# Default lists for host-specific configurations
#############################

DEFAULT_INSTALLED_APPS = (
    # Django modules
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    # Third-party modules
    'pipeline',
    'widget_tweaks',
    # Project modules
    'chachatwilio.common',
    'chachatwilio.auth',
    'chachatwilio.portal',
)

DEFAULT_MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

DEFAULT_TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.contrib.auth.context_processors.auth',
            'django.template.context_processors.media',
            'django.template.context_processors.static',
            'django.template.context_processors.tz',
            'django.contrib.messages.context_processors.messages',
            'django.template.context_processors.request',
            'chachatwilio.common.handlers.processors.template',
        ],
        'debug': os.environ.get('CHACHATWILIO_TEMPLATE_DEBUG', 'False') == 'True'
    },
}]

#############################
# Django configuration
#############################

# Application definition

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
AUTH_USER_MODEL = 'chachatwilio_auth.User'
LOGIN_URL = '/login'
LOGOUT_URL = '/logout'
ROOT_URLCONF = 'conf.urls'
WSGI_APPLICATION = 'conf.wsgi.application'

HOSTNAME = socket.gethostname()

# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
USE_TZ = True
HE_DATE_STRING = "%Y-%m-%d"
HE_TIME_STRING = "%H:%M:%S"
HE_DATE_TIME_STRING = HE_DATE_STRING + " " + HE_TIME_STRING

# Email settings


ADMIN_EMAIL_ADDRESS = os.environ.get('CHACHATWILIO_ADMIN_EMAIL')
SERVER_EMAIL = ADMIN_EMAIL_ADDRESS
EMAIL_USE_TLS = os.environ.get('CHACHATWILIO_EMAIL_USE_TLS', 'True') == 'True'
EMAIL_PORT = os.environ.get('CHACHATWILIO_EMAIL_PORT')
EMAIL_ADDRESS = os.environ.get('CHACHATWILIO_CONTACT_EMAIL')
DEFAULT_FROM_EMAIL = '{} <{}>'.format(PROJECT_NAME, EMAIL_ADDRESS)
EMAIL_HOST = os.environ.get('CHACHATWILIO_EMAIL_HOST')

EMAIL_HOST_USER = os.environ.get('CHACHATWILIO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('CHACHATWILIO_EMAIL_HOST_PASSWORD')

# Authentication

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Security

SECRET_KEY = os.environ.get('CHACHATWILIO_SECRET_KEY')
CSRF_COOKIE_SECURE = os.environ.get('CHACHATWILIO_CSRF_COOKIE_SECURE', 'True') == 'True'
SESSION_COOKIE_SECURE = os.environ.get('CHACHATWILIO_SESSION_COOKIE_SECURE', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('CHACHATWILIO_ALLOWED_HOSTS').split(' ')
CSRF_MIDDLEWARE_SECRET = os.environ.get('CHACHATWILIO_CSRF_MIDDLEWARE_SECRET')

# Logging

DEBUG = os.environ.get('CHACHATWILIO_DEBUG', 'False') == 'True'

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'pipeline.finders.PipelineFinder',
)

# Media files

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Pipelines

PIPELINE = {
    'DISABLE_WRAPPER': True,
    'STYLESHEETS': {
    },
    'JAVASCRIPT': {
        'base': {
            'source_filenames': (
                'js/vendors/moment.js',
                'js/vendors/moment-timezone.js',
            ),
            'output_filename': 'js/chachatwilio_{}.min.js'.format(PROJECT_VERSION)
        },
    }
}

# Twilio

TWILIO_ACCOUNT_SID = os.environ.get('CHACHATWILIO_TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('CHACHATWILIO_TWILIO_AUTH_TOKEN')
TWILIO_SMS_FROM = os.environ.get('CHACHATWILIO_TWILIO_SMS_FROM')
