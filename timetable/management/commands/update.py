# encoding: utf-8
import operator

from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.db.models import Q
from django.core.files.base import ContentFile

from timetable import scraper
from timetable import ical
from timetable.models import DegreeSubject, Calendar, Lesson


class Command(NoArgsCommand):
    help = "Populate DB. Slow. Run this on setup"

    def handle_noargs(self, **options):
        if not settings.ACADEMIC_YEAR or not settings.TERM:
            raise ValueError("ACADEMIC_YEAR or TERM undefined in settings.")
        # Get all DegreeSubjects which have an active calendar AND are currently
        # active due to academic year and term
        degree_subjects = DegreeSubject.objects.exclude(calendar=None).filter(
            academic_year=settings.ACADEMIC_YEAR,
            term_key=settings.TERM
        )
        self.stdout.write("Updating lessons. This will take a while...\n")
        scraper.populate_lessons(degree_subjects)
        self.stdout.write("DONE!\n")
        self.stdout.write("Updating calendars. This may also take a while...\n")
        calendars = Calendar.objects.filter(degree_subjects__in=degree_subjects)
        for calendar in calendars:
            q_list = []
            for ds in calendar.degree_subjects.all():
                q = Q(
                    subject=ds.subject,
                    group_key=ds.group_key,
                    academic_year=settings.ACADEMIC_YEAR)
                q_list.append(q)
            lessons_filter = reduce(operator.or_, q_list)
            lessons = Lesson.objects.filter(lessons_filter)
            calendar.file.save(calendar.name + '.ics',
                ContentFile(ical.generate(lessons)))
        self.stdout.write("DONE!\n")
