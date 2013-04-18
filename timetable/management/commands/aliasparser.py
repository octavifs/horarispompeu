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
from django.db import IntegrityError
import requests
from timetable.models import Subject, SubjectAlias
from timetable.sources.esup import *
import _parser as parser


class Command(NoArgsCommand):
    help = "Parse classes and subjects from the ESUP degrees"

    def handle_noargs(self, **options):
        for degree, years in COMPULSORY_SUBJECTS_TIMETABLES.iteritems():
            for year, terms in years.iteritems():
                for term, groups in terms.iteritems():
                    for group, url, _ in groups:
                        print url
                        html = requests.get(url).text
                        self.parse(html)
        for term, groups in OPTIONAL_SUBJECTS_TIMETABLES.iteritems():
            for group, url, _ in groups:
                print url
                html = requests.get(url).text
                self.parse(html)

    def parse(self, html):
        classes = parser.parse(html)
        aliases = set([entry.subject for entry in classes])
        for alias in aliases:
            entries = SubjectAlias.objects.filter(name=alias)
            if len(entries) != 0:
                continue  # Nothing to do here
            subjectalias = SubjectAlias(name=alias, subject=None)
            subjectalias.save()
