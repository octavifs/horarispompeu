from django.conf.urls import patterns, url

from esup import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
)
