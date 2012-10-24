import socket
import os


USE_EMBER_STYLE_ATTRS = True

# TODO: This is not very safe.
SESSION_COOKIE_HTTPONLY = False

SESSION_COOKIE_SECURE = True

# Workaround - Django requests pages over HTTP after logging in
LOGIN_REDIRECT_URL = 'https://django-socketio-chat.local'

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = ()
MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'database',
        'USER': 'username',
        'PASSWORD': 'password',
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

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

ROOT_URLCONF = 'urls'
LOGIN_URL = '/admin/'

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
