import os
import sys
from datetime import datetime

sys.path.insert(0, '../../example')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from tornadio2 import SocketConnection, TornadioRouter, SocketServer, event
from tornado import web

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.core.serializers import json
from django.utils.html import strip_tags

from django_socketio_chat.serializers import ChatSerializer
from django_socketio_chat.models import Chat


class ChatConnection(SocketConnection):

    connections = set()

    def on_open(self, info):
        """
        Find the Django user corresponding to this connection and send back useful chat info.
        """

        # TODO: keep a list of connections and corresponding Users

        # get Django session
        cookie = info.get_cookie('sessionid')
        if cookie:
            # get User for session
            session = Session.objects.get(session_key=cookie.value)
            uid = session.get_decoded().get('_auth_user_id')
            try:
                self.user = User.objects.get(pk=uid)

                self.emit('welcome', self.user.username)
                self.connections.add(self)

                for connection in self.connections:
                    # TODO: only send this to users who can see the joined user
                    connection.emit('user_joined', self.user.username)

                # find all logged in users
                users = []
                sessions = Session.objects.filter(expire_date__gte=datetime.now())
                logged_in_user_ids = filter(None, list(set([ session.get_decoded().get('_auth_user_id') for session in sessions ])))

                for user in User.objects.all():
                    users.append({
                        'id': user.id, 'username': user.username, 'online': user.id in logged_in_user_ids
                    })
                self.emit('users', users)

            except User.DoesNotExist:
                pass

    @event
    def chat_start(self, usernames):
        users = User.objects.filter(username__in=usernames)
        chat = Chat.start(self.user, list(users))

        # serialize the chat to JSON
        serializer = ChatSerializer(chat)
        serialized_chat = serializer.data

        # Tornadio's JSON encoder is not python datetime aware
        serialized_chat['started'] = json.simplejson.dumps(serialized_chat['started'], cls=json.DjangoJSONEncoder).strip('"')

        # TODO: don't send this to all connections, just to the connection of the users of the chat
        for connection in self.connections:
            connection.emit('chat_start_success', serialized_chat)

    @event
    def message(self, message):
        message = strip_tags(message)
        for connection in self.connections:
            connection.emit('message', self.user.username, message)

    @event
    def leave(self):
        self.connections.remove(self)
        for connection in self.connections:
            connection.emit('user_left', self.user.username)

    def on_disconnect(self):
        self.leave()

    def on_close(self):
        pass


# Create chat router
ChatRouter = TornadioRouter(ChatConnection, user_settings={'websocket_check': True}, namespace='chat/socket.io')

# Create application
application = web.Application(
    ChatRouter.apply_routes([]),
    socket_io_port = 8001,
)

if __name__ == "__main__":
    #import logging
    #logging.getLogger().setLevel(logging.DEBUG)

    SocketServer(application)
