from settings_default import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'd-socketio-chat',
        'USER': 'root',
        'PASSWORD': 'my5q1',
        'HOST': '',
        'PORT': '',
    }
}

LOGIN_REDIRECT_URL = '/'

