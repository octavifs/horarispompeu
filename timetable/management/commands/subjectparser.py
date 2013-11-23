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
import os
import json

import requests
from django.core.management.base import NoArgsCommand
from django.conf import settings

from timetable.models import Faculty, Subject, SubjectAlias, SubjectDuplicate, AcademicYear, Degree
import _parser as parser
import operations


FILEPATH = os.path.dirname(__file__)
SUBJECTS_FILEPATH = os.path.join(FILEPATH, "../../sources/subjects.json")
TIMETABLES_FILEPATH = os.path.join(FILEPATH, "../../sources/timetables.json")


class Command(NoArgsCommand):
    help = (
        "Add subjects to the database.\nAdds Subject objects, necessary "
        "SubjectAlias models and creates DegreeSubjects linking degree with "
        "a subject, so the UI chooser works OK. This command may fail, since "
        "it parses the remote timetables and, apart from not being available "
        "it may happen that some aliases are not correctly filled, so we dont "
        "know which subject a lesson is referring to and the script fails.\n"
        "If that happens, fill the aliases with its corresponding subject and "
        "run the script again."
    )

    def handle_noargs(self, **options):
        # First, create all the subjects and related Aliases (if missing)
        self.stdout.write("Opening subjects file...")
        with open(SUBJECTS_FILEPATH, 'r') as subjects_file:
            faculty_subjects = json.load(subjects_file, encoding="utf-8")
            for faculty, subjects in faculty_subjects.iteritems():
                faculty_entry, created = Faculty.objects.get_or_create(name=faculty)
                for subject in subjects:
                    self.stdout.write("Processing subject {} for faculty {}: "
                        .format(subject, faculty), ending="")
                    # Search if that subject had been deleted from the database
                    # (because it was a duplicate)
                    duplicates = SubjectDuplicate.objects.filter(
                        faculty=faculty_entry,
                        name=subject)
                    if duplicates.exists():  # If duplicates exist, skip subject
                        self.stdout.write("DUPLICATE")
                        continue
                    # Create or get the subject entry
                    subject_entry, created = Subject.objects.get_or_create(
                        faculty=faculty_entry, name=subject)
                    # Create or get the alias entry
                    subject_alias, created = SubjectAlias.objects.get_or_create(
                        name=subject,
                        subject=subject_entry)
                    self.stdout.write("CREATED" if created else "OK")
        self.stdout.write("Closing subjects file.")
        # Now, parse the timetables, and add all missing SubjectAlias and
        # DegreeSubjects.
        self.stdout.write("Opening timetables file...")
        with open(TIMETABLES_FILEPATH, 'r') as timetables_file:
            degree_years = json.load(timetables_file, encoding="utf-8")
            new_subjectaliases = False
            for entry in degree_years:
                # Don't process timetables that don't belong to the current year
                if entry["academic_year"] != settings.ACADEMIC_YEAR:
                    continue
                for timetable in entry["timetables"]:
                    # Don't process timetables that don't belong to the current
                    # term
                    if timetable["term"] != settings.TERM:
                        continue
                    self.stdout.write("Processing {} aliases: "
                        .format(timetable["filename"]), ending="")
                    # Download the timetable and parse its lessons
                    r = requests.get(timetable["url"])
                    timetable["lessons"] = list(parser.parse(r.text))
                    created = operations.insert_subjectaliases(timetable["lessons"])
                    self.stdout.write("NEW" if created else "OK")
                    new_subjectaliases = new_subjectaliases or created
            # Check if some aliases have been added
            if new_subjectaliases:
                self.stderr.write(
                    "ERROR: some SubjectAliases are empty. Fill them "
                    "using the admin interface before proceeding")
                return
            # Iterate over the json again, and now add DegreeSubjects
            for entry in degree_years:
                # Don't process timetables that don't belong to the current year
                if entry["academic_year"] != settings.ACADEMIC_YEAR:
                    continue
                faculty_entry, created = Faculty.objects.get_or_create(
                    name=entry["faculty"])
                academic_year_entry, created = AcademicYear.objects.get_or_create(
                    year=entry["academic_year"])
                degree_entry, created = Degree.objects.get_or_create(
                    faculty=faculty_entry, name=entry["degree"])
                for timetable in entry["timetables"]:
                    # Don't process timetables that don't belong to the current
                    # term
                    if timetable["term"] != settings.TERM:
                        continue
                    self.stdout.write("Processing {} degree subjects: "
                        .format(timetable["filename"]), ending="")
                    # This will insert the missing degreesubjects
                    created = operations.insert_degreesubjects(
                        timetable["lessons"],
                        timetable["group"],
                        academic_year_entry,
                        degree_entry,
                        timetable["year"],
                        timetable["term"])
                    self.stdout.write("NEW" if created else "OK")
