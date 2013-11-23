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

import io
import os
import json

import requests
from django.core.management.base import NoArgsCommand
from django.conf import settings
from timetable import operations
from timetable import parser

from timetable.models import *

FILEPATH = os.path.dirname(__file__)
TIMETABLES_FILEPATH = os.path.join(FILEPATH, "../../sources/timetables.json")


class Command(NoArgsCommand):
    help = (
        "Parse lessons from ESUP timetables."
    )

    def handle_noargs(self, **options):
        global TIMETABLES_FILEPATH
        with open(TIMETABLES_FILEPATH, 'r') as f:
            timetables = json.load(f, encoding="utf-8")
        for entry in timetables:
            # Don't process timetables that don't belong to the current year
            if entry["academic_year"] != settings.ACADEMIC_YEAR:
                    continue
            # Each entry has a faculty, academic year and degree. It also
            # has a list of timetables.
            # First, we make sure that the basic info is in the system
            faculty, _ = Faculty.objects.get_or_create(name=entry["faculty"])
            if not AcademicYear.objects.filter(year=entry["academic_year"]).exists():
                AcademicYear(entry["academic_year"]).save()
            if not Degree.objects.filter(faculty=faculty, name=entry["degree"]).exists():
                Degree(faculty=faculty, name=entry["degree"]).save()
            # Now that everything is initialized, start going through timetables
            for schedule in entry["timetables"]:
                # Don't process timetables that don't belong to the current
                # term
                if schedule["term"] != settings.TERM:
                    continue
                self.update(
                    entry["faculty"],
                    entry["academic_year"],
                    entry["degree"],
                    schedule["year"],
                    schedule["term"],
                    schedule["group"],
                    schedule["url"],
                    os.path.join(settings.TIMETABLE_ROOT, schedule["filename"])
                )

    def update(self, faculty, academic_year, degree, year, term, group, url, file_path, overwrite=True):
        """
        Updates Lessons in the DB. Deletes outdated lessons and adds the new
        entries.
        """
        self.stdout.write("Downloading {}... ".format(url), ending="")
        # Get HTML from the ESUP website
        r = requests.get(url)
        new_html = r.text
        self.stdout.write("DONE")
        # Get HTML from previous run
        try:
            f = io.open(file_path, encoding='utf-8')
            old_html = f.read()
            f.close()
        except IOError:
            # If old html could not be opened. Alert about it but go on
            self.stdout.write("Could not open {}".format(file_path))
            old_html = ""
        # Parse old html into a set of parser.Lessons
        old_lessons = set(parser.parse(old_html))
        # Parse new html into a set of parser.Lessons
        new_lessons = set(parser.parse(new_html))
        # Check for differences. If equal, no need to process it.
        if old_lessons == new_lessons:
            self.stdout.write("No changes since last update.")
            return
        self.stdout.write("Updating...")
        # Compute deleted & the inserted lessons.
        deleted_lessons = old_lessons - new_lessons  # set difference
        inserted_lessons = new_lessons - old_lessons  # set difference
        modified_lessons = old_lessons ^ new_lessons  # set symmetric difference
        # Add SubjectAlias if necessary
        created = operations.insert_subjectaliases(modified_lessons)
        if created:
            self.stdout.write("Added some missing SubjectAliases")
        academic_year_entry = AcademicYear.objects.get(year=academic_year)
        # Delete outdated lessons
        deleted = operations.delete_lessons(deleted_lessons, group,
                                            academic_year_entry)
        if deleted:
            self.stdout.write("Some Lessons were deleted")
        # Insert updated lessons
        inserted = operations.insert_lessons(inserted_lessons, group,
                                             academic_year_entry)
        if inserted:
            self.stdout.write("Some Lessons were inserted")
        # Update old HTML
        try:
            if overwrite:
                f = io.open(file_path, 'w', encoding="utf-8")
                f.write(new_html)
                f.close()
                self.stdout.write("HTML written to {}".format(file_path))
        except IOError:
            # If old html could not be written. Alert about it but go on
            self.stderr("Could not write to {}. HTML not updated".format(file_path))
