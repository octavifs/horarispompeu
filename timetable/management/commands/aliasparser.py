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
from django.core.management.base import BaseCommand
from timetable.models import SubjectAlias, Faculty, AcademicYear, Degree
import _parser as parser
import os
import json
import requests

FILEPATH = os.path.dirname(__file__)
TIMETABLES_FILEPATH = os.path.join(FILEPATH, "../../sources/timetables.json")


class Command(BaseCommand):
    help = "Parse classes and subjects from the ESUP degrees"

    def handle(self, *args, **options):
        global TIMETABLES_FILEPATH
        if args:
            TIMETABLES_FILEPATH = args[0]
        with open(TIMETABLES_FILEPATH, 'r') as f:
            timetables = json.load(f, encoding="utf-8")
        for entry in timetables:
            # Each entry has a faculty, academic year and degree. It also
            # has a list of timetables.
            # First, we make sure that the basic info is in the system
            try:
                faculty = Faculty.objects.get(name=entry["faculty"])
            except Faculty.DoesNotExist:
                faculty = Faculty(entry["faculty"])
                faculty.save()
            if not AcademicYear.objects.filter(year=entry["academic_year"]).exists():
                AcademicYear(entry["academic_year"]).save()
            if not Degree.objects.filter(faculty=faculty, name=entry["degree"]).exists():
                Degree(faculty=faculty, name=entry["degree"]).save()
            # Now that everything is initialized, start going through timetables
            for timetable in entry["timetables"]:
                print timetable["url"]
                html = requests.get(timetable["url"]).text
                self.parse(html)

    def parse(self, html):
        classes = parser.parse(html)
        aliases = set([entry.subject for entry in classes])
        for alias in aliases:
            entries = SubjectAlias.objects.filter(name=alias)
            if entries.exists():
                continue  # Nothing to do here
            subjectalias = SubjectAlias(name=alias, subject=None)
            subjectalias.save()
