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

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.db.models.query import QuerySet
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models import Q
from timetable.models import *
import requests
import io
import os
import json
import operator
from timetable.sources.esup import *
import _parser as parser
import timetable.calendar

FILEPATH = os.path.dirname(__file__)
TIMETABLES_FILEPATH = os.path.join(FILEPATH, "../../sources/timetables.json")


class Command(BaseCommand):
    help = "Parse lessons and subjects from the ESUP degrees"

    def handle(self, *args, **options):
        global TIMETABLES_FILEPATH
        # Empty QuerySet that will hold all modified DegreeSubjects
        modified_degreesubjects = QuerySet(model=DegreeSubject)
        if args:
            TIMETABLES_FILEPATH = args[0]
        with open(TIMETABLES_FILEPATH, 'r') as f:
            timetables = json.load(f, encoding="utf-8")
        for entry in timetables:
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
                # This is a set union. Union of modified degreesubjects in the
                # modified_degreesubjects QuerySet
                modified_degreesubjects = modified_degreesubjects | self.update(
                    entry["faculty"],
                    entry["academic_year"],
                    entry["degree"],
                    schedule["year"],
                    schedule["term"],
                    schedule["group"],
                    schedule["url"],
                    os.path.join(settings.TIMETABLE_ROOT, schedule["filename"])
                )
        # Only update calendars (.ics files) that have been modified.
        self.update_calendars(modified_degreesubjects)

    def update(self, faculty, academic_year, degree, year, term, group, url, file_path, overwrite=True):
        print("")
        print(url)
        # Get HTML from the ESUP website
        r = requests.get(url)
        new_html = r.text
        # Get HTML from previous run
        try:
            f = io.open(file_path, encoding='utf-8')
            old_html = f.read()
            f.close()
        except IOError:
            # If old html could not be opened. Alert about it but go on
            print("Could not open " + file_path)
            old_html = ""
        # Check for differences. If equal, no need to process it.
        if hash(old_html) == hash(new_html):
            print("\tNo changes since last update...")
            return QuerySet(model=DegreeSubject)
        print("\tUpdating...")
        # Parse old html into a set of parser.Lessons
        old_lessons = set(parser.parse(old_html))
        # Parse new html into a set of parser.Lessons
        new_lessons = set(parser.parse(new_html))
        # Compute deleted & the inserted lessons.
        deleted_lessons = old_lessons - new_lessons  # set difference
        inserted_lessons = new_lessons - old_lessons  # set difference
        # Delete outdated lessons
        self.delete(deleted_lessons, faculty, academic_year, degree, year, term, group)
        # Insert updated lessons
        self.insert(inserted_lessons, faculty, academic_year, degree, year, term, group)
        # Update old HTML
        try:
            if overwrite:
                f = io.open(file_path, 'w', encoding="utf-8")
                f.write(new_html)
                f.close()
        except IOError:
            # If old html could not be written. Alert about it but go on
            print("Could not write " + file_path)
            print("HTML not updated")
        #
        # Create a list of modified DegreeSubjects
        #
        # First, collect changed lessons
        modified_lessons = deleted_lessons | inserted_lessons  # set union
        # If no lessons modified, return an empty QuerySet
        if not modified_lessons:
            return QuerySet(model=DegreeSubject)
        # select SubjectAlias that contain a subject that has changed
        q_list = (Q(name=lesson.subject) for lesson in modified_lessons)
        modified_subjectaliases = SubjectAlias.objects.filter(reduce(operator.or_, q_list))
        # select all Subjects referred by its SubjectAlias
        q_list = (Q(subject=alias.subject) for alias in modified_subjectaliases)
        modified_degreesubjects = DegreeSubject.objects.filter(reduce(operator.or_, q_list))
        return modified_degreesubjects

    def delete(self, deleted_lessons, faculty, academic_year, degree, year, term, group):
        academic_year = AcademicYear.objects.get(year=academic_year)
        for entry in deleted_lessons:
            alias = entry.subject
            try:
                subject = SubjectAlias.objects.get(name=alias).subject
            except SubjectAlias.DoesNotExist, e:
                raise e
            try:
                lesson = Lesson.objects.get(
                    subject=subject,
                    group=group,
                    subgroup=entry.group,
                    kind=entry.kind,
                    room=entry.room,
                    date_start=entry.date_start,
                    date_end=entry.date_end,
                    academic_year=academic_year
                )
                lesson.delete()
            except Lesson.DoesNotExist:
                pass

    def insert(self, inserted_lessons, faculty, academic_year, degree, year, term, group):
        faculty = Faculty.objects.get(name=faculty)
        academic_year = AcademicYear.objects.get(year=academic_year)
        # create degreesubjects
        for entry in inserted_lessons:
            alias = entry.subject
            try:
                subject = SubjectAlias.objects.get(name=alias).subject
            except SubjectAlias.DoesNotExist, e:
                raise e
            degree_obj = Degree.objects.get(name=degree, faculty=faculty)
            degreesubject = DegreeSubject(
                subject=subject,
                degree=degree_obj,
                academic_year=academic_year,
                year=year,
                term=term,
                group=group
            )
            try:
                degreesubject.save()
            except IntegrityError:
                # This will trigger when trying to add a duplicate entry
                pass
        # create lessons
        for entry in inserted_lessons:
            alias = entry.subject
            subject = SubjectAlias.objects.get(name=alias).subject
            lesson = Lesson(
                subject=subject,
                group=group,
                subgroup=entry.group,
                kind=entry.kind,
                room=entry.room,
                date_start=entry.date_start,
                date_end=entry.date_end,
                academic_year=academic_year,
                raw_entry=entry.raw_data,
            )
            try:
                lesson.save()
            except IntegrityError:
                # This will trigger when trying to add a duplicate entry
                pass

    def update_calendars(self, degree_subjects):
        calendars = Calendar.objects.filter(degree_subjects=degree_subjects)
        for calendar in calendars:
            lessons = QuerySet(model=Lesson)
            for degreesubject in calendar.degree_subjects.all():
                lessons = lessons | degreesubject.lessons()
            lessons = lessons.distinct()
            #lessons = reduce(operator.or_, calendar.degree_subjects.lessons)
            calendar_string = timetable.calendar.generate(lessons)
            try:
                calendar.file.delete()
            except OSError:
                # File already deleted. No need to do anything.
                pass
            calendar.file.save(calendar.name + '.ics',
                               ContentFile(calendar_string))
