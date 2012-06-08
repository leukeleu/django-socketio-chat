from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin

from my_site.views import Home

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url("chat/", include("django_socketio_chat.urls")),
    url('^$', Home.as_view())
)
