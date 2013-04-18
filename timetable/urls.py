# Copyright (C) 2013  Octavi Font <octavi.fs@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
