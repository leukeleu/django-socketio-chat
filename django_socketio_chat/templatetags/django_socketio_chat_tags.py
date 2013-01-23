from django.conf import settings
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def django_socketio_chat_is_debug(context):
    context['debug'] = settings.DEBUG
    return ''
