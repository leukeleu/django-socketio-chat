import os

# TODO: This is not very safe.
SESSION_COOKIE_HTTPONLY = False

SESSION_COOKIE_SECURE = True

# let Django know that all requests are secure
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DEBUG = False
TEMPLATE_DEBUG = DEBUG
ADMINS = ()
MANAGERS = ADMINS

DATABASES = {}

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

ROOT_URLCONF = 'example.urls'
WSGI_APPLICATION = 'example.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_socketio_chat',
    'my_site',
)

LOGIN_REDIRECT_URL = '/'
