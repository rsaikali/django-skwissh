# -*- coding: utf-8 -*-
# Django settings for testproject.

import os
PROJECT_ROOT = os.path.dirname(__file__)
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Skwissh contact', 'contact@skwissh.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_ROOT, 'skwissh.db'),
        'TEST_NAME': os.path.join(PROJECT_ROOT, 'skwissh_unittests.db'),
    },
}
TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'fr'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)
SECRET_KEY = ')d-dvd7(tmj-y95z(yhd$jzsqwvtk4psr0pkyz!-y25$ij(u=9'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)
ROOT_URLCONF = 'testproject.urls'
WSGI_APPLICATION = 'testproject.wsgi.application'
TEMPLATE_DIRS = ()
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'kronos',
    'skwissh',
)
LANGUAGES = (("fr", "Français"), ("en", "English"),)
