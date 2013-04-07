# encoding: utf-8
from __future__ import unicode_literals
from django.core.management.base import NoArgsCommand
from django.db import IntegrityError
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
                    for group, url in groups:
                        print url
                        html = requests.get(url).text
                        self.parse(degree, year, term, group, html)
                        print ""
        for degree in COMPULSORY_SUBJECTS_TIMETABLES:
            for term, groups in OPTIONAL_SUBJECTS_TIMETABLES.iteritems():
                for group, url in groups:
                    print url
                    html = requests.get(url).text
                    self.parse(degree, year, term, group, html)
                    print ""

    def parse(self, degree, year, term, group, html):
        esup = Faculty.objects.get(name='ESUP')
        academic_year = AcademicYear(year='2012-13')
        lessons = parser.parse(html)
        # create degreesubjects
        for entry in lessons:
            alias = entry.subject
            subject = SubjectAlias.objects.filter(name=alias)[0].subject
            degree_obj = Degree.objects.filter(name=degree, faculty=esup)[0]
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
            except Exception:
                pass
        # create lessons
        for entry in lessons:
            alias = entry.subject
            subject = SubjectAlias.objects.filter(name=alias)[0].subject
            degree_obj = Degree.objects.filter(name=degree, faculty=esup)[0]
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
            except Exception, e:
                print e
