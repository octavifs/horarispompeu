# encoding: utf-8
from __future__ import unicode_literals
from django.core.management.base import NoArgsCommand
from django.db.utils import IntegrityError
import requests
from timetable.models import *
from _esup_timetable_data import *
import _parser as parser


class Command(NoArgsCommand):
    help = "Parse lessons and subjects from the ESUP degrees"

    def handle_noargs(self, **options):
        for degree, years in COMPULSORY_SUBJECTS_TIMETABLES.iteritems():
            for year, terms in years.iteritems():
                for term, groups in terms.iteritems():
                    for group, url, file_path in groups:
                        self.update(
                            degree,
                            year,
                            term,
                            group,
                            url,
                            file_path
                        )
        for degree in COMPULSORY_SUBJECTS_TIMETABLES:
            for term, groups in OPTIONAL_SUBJECTS_TIMETABLES.iteritems():
                for group, url, file_path in groups:
                    self.update(
                        degree,
                        "optatives",
                        term,
                        group,
                        url,
                        file_path
                    )

    def update(self, degree, year, term, group, url, file_path):
        print ""
        print url
        # Get HTML from the ESUP website
        new_html = requests.get(url).text
        new_html = new_html.encode('UTF-8')
        # Get HTML from previous run
        try:
            f = open(file_path)
            old_html = f.read()
            f.close()
        except IOError:
            # If old html could not be opened. Alert about it but go on
            print "Could not open " + file_path
            old_html = ""
        # Check for differences. If equal, no need to process it.
        if hash(old_html) == hash(new_html):
            print "\tNo changes since last update..."
            return
        print "\tUpdating..."
        # Parse old html into a set of parser.Lessons
        old_lessons = set(parser.parse(old_html))
        # Parse new html into a set of parser.Lessons
        new_lessons = set(parser.parse(new_html))
        # Compute deleted & the inserted lessons.
        deleted_lessons = old_lessons - new_lessons
        inserted_lessons = new_lessons - old_lessons
        # Delete outdated lessons
        self.delete(deleted_lessons, degree, year, term, group)
        # Insert updated lessons
        self.insert(inserted_lessons, degree, year, term, group)
        # Update old HTML
        try:
            f = open(file_path, 'w')
            f.write(new_html)
            f.close()
        except IOError:
            # If old html could not be written. Alert about it but go on
            print "Could not write " + file_path
            print "HTML not updated"

    def delete(self, deleted_lessons, degree, year, term, group):
        academic_year = AcademicYear.objects.get(year='2012-13')
        for entry in deleted_lessons:
            alias = entry.subject
            subject = SubjectAlias.objects.filter(name=alias)[0].subject
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

    def insert(self, inserted_lessons, degree, year, term, group):
        faculty = Faculty.objects.get(name='ESUP')
        academic_year = AcademicYear(year='2012-13')
        # create degreesubjects
        for entry in inserted_lessons:
            alias = entry.subject
            subject = SubjectAlias.objects.get(name=alias).subject
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
