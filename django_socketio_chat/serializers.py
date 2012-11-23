from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.fields import Field, CharField

from .models import Chat, UserChatStatus, Message


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

class UserSerializer(serializers.ModelSerializer):
    # TODO: add `availability` field / property to User (via UserProfile?): availability = Field(source='get_availability')

    class Meta:
        model = User
        fields = ('username',)


# ---[ viewpoint = Chat ]--- #

class UserChatStatusSerializer(UUIDFieldSerializerMixin, serializers.ModelSerializer):
    user__username = Field(source='user.username')

    class Meta:
        model = UserChatStatus
        fields = ('user__username', 'status', 'joined', 'left', 'unseen_message_count')


class ChatMessageSerializer(UUIDFieldSerializerMixin, serializers.ModelSerializer):
    user__username = Field(source='user.username')

    class Meta:
        model = Message
        fields = ('timestamp', 'user__username', 'message',)


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
    user__username = Field(source='user.username')

    class Meta:
        model = Message
        fields = ('uuid', 'timestamp', 'chat__uuid', 'user__username', 'message',)
