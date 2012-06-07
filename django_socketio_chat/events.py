from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

from django_socketio import events


@events.on_connect
def connect(request, socket, context):
    """
    Do some handshaking in a future version.
    Handshaking is implemented in the latest socket.io versin, as well as gevent-socket.io,
    but not yet in django_socketio.
    """
    print request.user


@events.on_message
def message(request, socket, context, message):
    """
    * go-online
    * go-offline

    * invite-user
    * leave-chat
    """

    if message.get('action') == 'authenticate':
        session_id = message.get('session_id')
        if session_id:
            # get user corresponding to session id
            session = Session.objects.get(session_key=session_id)
            uid = session.get_decoded().get('_auth_user_id')
            if not uid:
                # session was closed
                return
            try:
                user = User.objects.get(pk=uid)
               # print user.username, user.get_full_name(), user.email
            except User.DoesNotExist:
                # non existing user
                return

