from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.fields import Field, CharField

from .models import ChatSession, Chat, UserChatStatus, Message


class UUIDFieldSerializerMixin(serializers.ModelSerializer):
    """
    Django REST Framework does not know what to do with UUIDFields.
    TODO: can this be made into a real Mixin that doesn't inherit from the serializers.ModelSerializer base class?
    """
    def get_field(self, model_field):
        if (model_field.name == 'uuid'):
            return CharField()

        return super(UUIDFieldSerializerMixin, self).get_field(model_field)


# ---[ viewpoint = User ]--- #

class ChatSessionSerializer(serializers.ModelSerializer):
    username = Field(source='user.username')

    class Meta:
        model = ChatSession
        fields = ('username', 'status', 'ui_is_visible')


class UserSerializer(serializers.ModelSerializer):
    # TODO: add `availability` field / property to User (via UserProfile?): availability = Field(source='get_availability')

    status = serializers.SerializerMethodField('get_status')

    class Meta:
        model = User
        fields = ('username', 'status')

    def get_status(self, obj):
        pass

# ---[ viewpoint = Chat ]--- #

class UserChatStatusSerializer(UUIDFieldSerializerMixin, serializers.ModelSerializer):
    user = UserSerializer()
    unread_messages = Field(source='unread_messages')

    class Meta:
        model = UserChatStatus
        fields = ('user', 'status', 'joined', 'unread_messages')


class ChatMessageSerializer(UUIDFieldSerializerMixin, serializers.ModelSerializer):
    user_from__username = Field(source='user_from.username')
    chat__uuid = Field(source='chat.uuid')

    class Meta:
        model = Message
        fields = ('uuid', 'chat__uuid', 'timestamp', 'user_from__username', 'message_body',)


class ChatSerializer(UUIDFieldSerializerMixin, serializers.ModelSerializer):
    user_chat_statuses = UserChatStatusSerializer()
    messages = ChatMessageSerializer()

    class Meta:
        model = Chat
        queryset = Chat.objects.filter(uuid='74546e66ed5546ddb70faaca326a4b95')
        fields = ('uuid', 'started', 'user_chat_statuses', 'messages')


# ---[ viewpoint = Message ]-------- #

class MessageSerializer(UUIDFieldSerializerMixin, serializers.ModelSerializer):
    chat__uuid = Field(source='chat.uuid')
    user_from__username = Field(source='user_from.username')

    class Meta:
        model = Message
        fields = ('uuid', 'timestamp', 'chat__uuid', 'user_from__username', 'message_body',)
