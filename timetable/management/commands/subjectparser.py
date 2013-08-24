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
from django.db import IntegrityError
import os
import json
from timetable.models import Faculty, Subject, SubjectAlias, SubjectDuplicate


# Faculty names
FILEPATH = os.path.dirname(__file__)
SUBJECTS_FILEPATH = os.path.join(FILEPATH, "../../sources/subjects.json")


class Command(BaseCommand):
    help = "Parse subjects from the faculties and put them into the Database."
    args = "input subjects list (JSON format)"

    def handle(self, *args, **options):
        if args:
            subjects_file = open(args[0], 'r')
        else:
            subjects_file = open(SUBJECTS_FILEPATH, 'r')
        faculty_subjects = json.load(subjects_file, encoding="utf-8")
        for faculty, subjects in faculty_subjects.iteritems():
            # First of all, we add any missing faculty to the database
            # for faculty in self.faculties:
            try:
                faculty_entry = Faculty.objects.get(name=faculty)
            except Faculty.DoesNotExist:
                faculty_entry = Faculty(faculty)
                faculty_entry.save()
            for subject in subjects:
                # Search if that subject had been deleted from the database
                # (because it was a duplicate)
                duplicates = SubjectDuplicate.objects.filter(
                    faculty=faculty_entry,
                    name=subject)
                if duplicates.exists():  # If duplicates exist, skip subject
                    continue
                # Saves subject to the DB. If subject had already been saved,
                # retrieve it from the DB
                try:
                    subject_entry = Subject(faculty=faculty_entry, name=subject)
                    subject_entry.save()
                except IntegrityError:
                    subject_entry = Subject.objects.get(faculty=faculty_entry,
                                                        name=subject)
                # Creates an alias linking subject with the subject tuple
                # More aliases will be added manually later
                # If alias had already been saved, do nothing
                try:
                    subject_alias = SubjectAlias(
                        name=subject,
                        subject=subject_entry)
                    subject_alias.save()
                except IntegrityError:
                    pass
