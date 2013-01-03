from django.contrib.auth.models import User

from rest_framework import generics

from .models import Chat, Message
from .serializers import UserSerializer, ChatSerializer, MessageSerializer


class UserList(generics.ListAPIView):
    model = User
    serializer_class = UserSerializer

    def get_queryset(self):
        # TODO: only return users that the current user can 'see'
        return User.objects.all()


class ChatList(generics.ListCreateAPIView):
    model = Chat
    serializer_class = ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(users__username__contains=self.request.user.username)


class ChatDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Chat
    serializer_class = ChatSerializer
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_object(self, queryset=None):
        return super(ChatDetail, self).get_object(queryset=Chat.objects.filter(users__username__contains=self.request.user.username))


class MessageList(generics.ListCreateAPIView):
    model = Message
    serializer_class = MessageSerializer

    def get_queryset(self):
        return Message.objects.filter(chat__users__username__contains=self.request.user.username)


class MessageDetail(generics.RetrieveUpdateDestroyAPIView):
    model = Message
    serializer_class = MessageSerializer
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_object(self, queryset=None):
        return super(MessageDetail, self).get_object(queryset=Message.objects.filter(chat__users__username__contains=self.request.user.username))
