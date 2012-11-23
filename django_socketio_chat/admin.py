from django.contrib import admin

from .models import Chat, UserChatStatus, Message


class ChatAdmin(admin.ModelAdmin):
    pass


class UserChatStatusAdmin(admin.ModelAdmin):
    pass


class MessageAdmin(admin.ModelAdmin):
    pass


admin.site.register(Chat, ChatAdmin)
admin.site.register(UserChatStatus, UserChatStatusAdmin)
admin.site.register(Message, MessageAdmin)
