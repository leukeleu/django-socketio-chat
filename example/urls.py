from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin

from my_site.views import Home

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),

    url('^$', Home.as_view(), name='home'),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login', kwargs=dict(template_name='login.html')),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout', kwargs=dict(template_name='logged_out.html')),
)
