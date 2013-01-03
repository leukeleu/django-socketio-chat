import os
import sys

sys.path.insert(0, '../../example')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from tornadio2 import SocketConnection, TornadioRouter, SocketServer, event
from tornado import web

from rest_framework.renderers import JSONRenderer

from django.utils import simplejson
from django.utils.html import strip_tags

from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

from django_socketio_chat.models import Chat
from django_socketio_chat.serializers import UserSerializer, ChatSerializer, MessageSerializer


def prepare_for_emit(obj):
    """
    Prepare the object for emit() by Tornadio2's (too simple) JSON renderer
    - render to JSON using Django REST Framework 2's JSON renderer
    - convert back to _simple_ Python object using Django's simplejson
    """

    json = JSONRenderer().render(obj)

    return simplejson.loads(json)


class ChatConnection(SocketConnection):

    connections = set()

    def on_open(self, info):
        """
        Find the Django user corresponding to this connection and send back chat info.
        """

        # get Django session
        cookie = info.get_cookie('sessionid')
        if cookie:
            # get User for session
            session = Session.objects.get(session_key=cookie.value)
            user_id = session.get_decoded().get('_auth_user_id')
            try:
                # `store` user with connection
                self.user = User.objects.get(pk=user_id)

                self.emit('welcome', self.user.username)
                self.connections.add(self)

                # TODO: only send `user_join` event to visible users (as user status change)
                for connection in self.connections:
                    connection.emit('user_join', self.user.username)

                # TODO: determine visible users by connection (friends, groups, etc.) with the current user
                chat_users = User.objects.exclude(pk=self.user.pk)
                chat_users_obj = prepare_for_emit(UserSerializer(chat_users).data)
                self.emit('user_list', chat_users_obj)

                # TODO: filter using model methods?
                chats = Chat.objects.filter(users__id__contains=self.user.id)
                chats_obj = prepare_for_emit(ChatSerializer(chats).data)
                self.emit('chat_list', chats_obj)

            except User.DoesNotExist:
                pass

    @event
    def chat_create(self, usernames):
        users = User.objects.filter(username__in=usernames)
        # TODO: only start chat with visible users (filter)
        chat = Chat.start(self.user, list(users))
        chat_obj = prepare_for_emit(ChatSerializer(chat).data)

        for connection in self.connections:
            if connection.user in chat.users.all():
                connection.emit('chat_create', chat_obj)

    @event
    def message_req_create(self, message_body, chat_uuid):
        # TODO: only create message in visible chats
        chat = Chat.objects.get(uuid=chat_uuid)
        message = chat.add_message(self.user, strip_tags(message_body))
        message_obj = prepare_for_emit(MessageSerializer(message).data)

        for connection in self.connections:
            if connection.user in chat.users.all():
                connection.emit('message_create', message_obj)

    @event
    def leave(self):
        # TODO: only send `user_leave` event to visible users
        self.connections.remove(self)
        for connection in self.connections:
            connection.emit('user_leave', self.user.username)

    def on_disconnect(self):
        self.leave()

    def on_close(self):
        pass


# Create chat router
ChatRouter = TornadioRouter(ChatConnection, user_settings={'websocket_check': True}, namespace='chat/socket.io')

# Create application
application = web.Application(
    ChatRouter.apply_routes([]),
    socket_io_port=8001,
)

if __name__ == "__main__":
    # import logging
    # logging.getLogger().setLevel(logging.DEBUG)

    SocketServer(application)
