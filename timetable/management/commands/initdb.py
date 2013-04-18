# encoding: utf-8

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

from __future__ import unicode_literals
from django.core.management.base import NoArgsCommand

from timetable.models import Faculty, Degree, AcademicYear


class Command(NoArgsCommand):
    help = "Inserts basic initial data onto the DB."

    def handle_noargs(self, **options):
        esup = Faculty(name='ESUP')
        esup.save()
        Degree(
            faculty=esup,
            name='Grau en Enginyeria de Sistemes Audiovisuals'
        ).save()
        Degree(
            faculty=esup,
            name='Grau en Enginyeria de Telemàtica'
        ).save()
        Degree(
            faculty=esup,
            name='Grau en Enginyeria en Informàtica'
        ).save()
        AcademicYear(year='2012-13').save()
