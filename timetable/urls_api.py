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
from timetable import api

urlpatterns = patterns('',
    url(r'^faculty/$', api.faculty, name='faculty'),
    url(r'^faculty/(?P<pk>\w+)/$', api.faculty, name='faculty'),
    url(r'^degree/(?P<pk>\d+)/$', api.degree, name='degree'),
    url(r'^degree/$', api.degree, name='degree'),
    url(r'^lesson/$', api.lesson, name='lesson'),
    url(r'^subject/$', api.subject, name='subject'),
)
