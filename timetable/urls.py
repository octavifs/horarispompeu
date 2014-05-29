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
from django.views.generic import TemplateView
from timetable import views

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^facultat/$', views.FacultyList.as_view(), name='faculty'),
    url(r'^grau/$', views.DegreeList.as_view(), name='degree'),
    url(r'^curs/$', views.CourseList.as_view(), name='course'),
    url(r'^assignatures/$', views.SubjectView.as_view(), name='subject'),
    url(r'^calendari/$', views.CalendarView.as_view(), name='calendar'),
    url(r'^subscriu/$', views.subscription, name='subscription'),
    url(r'^pmf/$', TemplateView.as_view(template_name='pmf.html'), name='pmf'),
    url(r'^problemes/$', views.ContactView.as_view(), name='contact'),
    url(r'^gracies/$', TemplateView.as_view(template_name='thanks.html'),
        name='thanks'),
)
