from django.conf.urls import patterns, url

from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = patterns('',
    url(r'^users/$', views.UserList.as_view()),
    url(r'^chats/$', views.ChatList.as_view()),
    url(r'^chats/(?P<uuid>[0-9a-f]{32})/$', views.ChatDetail.as_view()),
    url(r'^chatsessions/(?P<username>\w+)/$', views.ChatSessionDetail.as_view()),
    url(r'^messages/$', views.MessageList.as_view()),
    url(r'^messages/(?P<uuid>[0-9a-f]{32})/$', views.MessageDetail.as_view())
)

urlpatterns = format_suffix_patterns(urlpatterns)
