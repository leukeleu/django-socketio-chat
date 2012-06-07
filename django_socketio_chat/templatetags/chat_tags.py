from django.template import Library
from django.contrib.auth.models import User
register = Library()


@register.inclusion_tag("django_socketio_chat.html", takes_context=True)
def chat(context, user):
    context["online_chat_contacts"] = []
    context["offline_chat_contacts"] = User.objects.all()
    context["chats"] = ['Chat 1', 'Chat 2', 'Chat 3']
    return context
