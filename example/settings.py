USE_EMBER_STYLE_ATTRS = True

#TODO: This is not very safe, but will do for now.
SESSION_COOKIE_HTTPONLY = False 

SESSION_COOKIE_SECURE = True

# workaround. Django requests pages over HTTP after logging in
LOGIN_REDIRECT_URL = 'https://meitnerium'

import os
DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = ()
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'chat',
        'USER': 'root',
        'PASSWORD': 'my5q1',
        'HOST': '',
        'PORT': '',
    }
}

SECRET_KEY = 'i_!&$f5@^%y*i_qa$*o&0$3q*1dcv^@_-l2po8-%_$_gwo+i-l'

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
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
ROOT_URLCONF = 'urls'
LOGIN_URL = '/admin/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'templatetag_handlebars',
    'django_socketio_chat',
    'my_site',
)

INSTALLED_APPS = ('debug_toolbar',) + INSTALLED_APPS

MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda x: True,
    'INTERCEPT_REDIRECTS': False
}

