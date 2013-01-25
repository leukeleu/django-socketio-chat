from django.conf import settings
from django.contrib.auth.models import User

USER_SETTINGS = getattr(settings, 'DJANGO_SOCKETIO_CHAT', None)

def users_that_i_see(user):
    if USER_SETTINGS and USER_SETTINGS.get('users_that_see_me'):
        return USER_SETTINGS['users_that_see_me'](user)
    return User.objects.all()

def users_that_see_me(user):
    if USER_SETTINGS and USER_SETTINGS.get('users_that_i_see'):
        return USER_SETTINGS['users_that_i_see'](user)
    return User.objects.all()
