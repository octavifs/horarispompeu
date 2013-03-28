from django.conf.urls import patterns, url
from django.http import HttpResponseRedirect
from django.views.generic.base import RedirectView


from timetable import views

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='grau')),
    url(r'^grau/$', views.degree, name='degree'),
    url(r'^curs/$', views.year, name='year'),
    url(r'^assignatures/$', views.subject, name='subject'),
    url(r'^calendari/$', views.calendar, name='calendar'),
)
