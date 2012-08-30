from django.conf.urls import patterns, include, url
urlpatterns = patterns('',
    url(r'^skwissh/', include('skwissh.urls')),
)
